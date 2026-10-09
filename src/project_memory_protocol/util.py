from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def sha256_file(path: Path, limit: int | None = None) -> str:
    digest = hashlib.sha256()
    remaining = limit
    with path.open("rb") as stream:
        while True:
            size = 1024 * 1024 if remaining is None else min(1024 * 1024, remaining)
            if size <= 0:
                break
            chunk = stream.read(size)
            if not chunk:
                break
            digest.update(chunk)
            if remaining is not None:
                remaining -= len(chunk)
    if remaining not in (None, 0):
        raise ValueError(f"{path} is shorter than the requested prefix")
    return digest.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_strings(item)


def estimated_tokens(text: str) -> int:
    """Cheap, deterministic estimate that handles Latin and CJK text."""
    ascii_count = sum(ord(char) < 128 for char in text)
    return max(1, int(ascii_count / 4 + (len(text) - ascii_count) / 1.5))


def safe_relative(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))


def resolve_inside(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    candidate.relative_to(root.resolve())
    return candidate

