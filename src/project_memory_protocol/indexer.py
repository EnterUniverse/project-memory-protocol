from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections.abc import Iterable
from pathlib import Path

from .config import Settings
from .util import iter_strings, sha256_file


def markdown_chunks(path: Path) -> Iterable[tuple[str, int, str]]:
    heading = path.name
    buffer: list[str] = []
    start = 1
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("#") and buffer:
            yield heading, start, "\n".join(buffer).strip()
            buffer, start = [], line_number
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
        buffer.append(line)
    if buffer:
        yield heading, start, "\n".join(buffer).strip()


def bounded_chunks(text: str, max_chars: int = 2400) -> Iterable[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    current: list[str] = []
    size = 0
    for paragraph in paragraphs:
        for piece_start in range(0, len(paragraph), max_chars):
            piece = paragraph[piece_start : piece_start + max_chars]
            if current and size + len(piece) + 2 > max_chars:
                yield "\n\n".join(current)
                current, size = [], 0
            current.append(piece)
            size += len(piece) + 2
    if current:
        yield "\n\n".join(current)


def extract_jsonl(path: Path) -> Iterable[tuple[str, str]]:
    with path.open(encoding="utf-8", errors="replace") as stream:
        for line_number, raw in enumerate(stream, 1):
            try:
                value = json.loads(raw)
            except json.JSONDecodeError:
                continue
            text = "\n".join(iter_strings(value)).strip()
            for part_number, part in enumerate(bounded_chunks(text)):
                if part:
                    yield f"jsonl:L{line_number}:part{part_number}", part


def curated_markdown(settings: Settings) -> list[Path]:
    return sorted(
        path
        for path in settings.memory_root.rglob("*.md")
        if settings.archive_root not in path.parents
    )


def build_index(settings: Settings, include_archive: bool = False) -> dict:
    settings.index_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = settings.index_path.with_suffix(".sqlite.tmp")
    temporary.unlink(missing_ok=True)
    database = sqlite3.connect(temporary)
    try:
        database.executescript(
            """
            CREATE TABLE chunks (
                id INTEGER PRIMARY KEY,
                source TEXT NOT NULL,
                locator TEXT NOT NULL,
                tier TEXT NOT NULL,
                authority INTEGER NOT NULL,
                source_sha256 TEXT NOT NULL,
                text TEXT NOT NULL,
                UNIQUE(source, locator, source_sha256)
            );
            CREATE VIRTUAL TABLE chunks_fts USING fts5(
                text, content='chunks', content_rowid='id', tokenize='unicode61'
            );
            """
        )
    except sqlite3.OperationalError as error:
        database.close()
        temporary.unlink(missing_ok=True)
        raise RuntimeError("SQLite FTS5 support is required") from error

    rows: list[tuple[str, str, str, int, str, str]] = []
    seen_text: set[str] = set()
    for path in curated_markdown(settings):
        relative = str(path.relative_to(settings.memory_root))
        tier = "stage" if "stages" in path.parts else "curated"
        authority = 80 if "modules" in path.parts else 70
        digest = sha256_file(path)
        for heading, line_number, text in markdown_chunks(path):
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            if text and text_hash not in seen_text:
                seen_text.add(text_hash)
                rows.append((relative, f"{heading}@L{line_number}", tier, authority, digest, text))

    if settings.claims_path.is_file():
        digest = sha256_file(settings.claims_path)
        for line_number, raw in enumerate(
            settings.claims_path.read_text(encoding="utf-8").splitlines(), 1
        ):
            if raw.strip():
                rows.append(
                    (
                        "claims/CLAIMS.jsonl",
                        f"claim@L{line_number}",
                        "claim",
                        95,
                        digest,
                        raw,
                    )
                )

    if include_archive:
        manifest = json.loads(settings.manifest_path.read_text(encoding="utf-8"))
        for record in manifest.get("records", []):
            path = settings.memory_root / record["archive_path"]
            if not path.is_file() or path.suffix.casefold() not in {".jsonl", ".json"}:
                continue
            for locator, text in extract_jsonl(path):
                text_hash = hashlib.sha256(text.encode()).hexdigest()
                if text_hash in seen_text:
                    continue
                seen_text.add(text_hash)
                rows.append((record["archive_path"], locator, "archive", 45, record["sha256"], text))

    database.executemany(
        "INSERT INTO chunks(source,locator,tier,authority,source_sha256,text) "
        "VALUES(?,?,?,?,?,?)",
        rows,
    )
    database.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild')")
    database.commit()
    database.close()
    temporary.replace(settings.index_path)
    return {"chunks": len(rows), "include_archive": include_archive}


def query_terms(query: str) -> str:
    terms = re.findall(r"[\w\u4e00-\u9fff]+", query.casefold())
    return " OR ".join(f'"{term}"' for term in terms if len(term) > 1)


def retrieve(settings: Settings, query: str, limit: int = 60) -> list[dict]:
    if not settings.index_path.is_file():
        build_index(settings, include_archive=False)
    expression = query_terms(query)
    if not expression:
        return []
    database = sqlite3.connect(settings.index_path)
    database.row_factory = sqlite3.Row
    rows = database.execute(
        """
        SELECT c.*, bm25(chunks_fts) AS lexical
        FROM chunks_fts JOIN chunks c ON c.id=chunks_fts.rowid
        WHERE chunks_fts MATCH ?
        ORDER BY (bm25(chunks_fts) - c.authority * 0.01) ASC
        LIMIT ?
        """,
        (expression, limit),
    ).fetchall()
    database.close()
    return [dict(row) for row in rows]

