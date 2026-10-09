from __future__ import annotations

import json
import os
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path

from .config import Settings
from .util import atomic_json, sha256_file

SOURCE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def utc_stamp() -> tuple[str, str]:
    now = datetime.now(UTC)
    return now.strftime("%Y%m%dT%H%M%S%fZ"), now.isoformat()


def load_json(path: Path, default: dict) -> dict:
    if not path.is_file():
        return default
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return value


def register_source(settings: Settings, source_id: str, path: Path, kind: str) -> None:
    if not SOURCE_ID.fullmatch(source_id):
        raise ValueError("source id must use letters, digits, dot, underscore, or hyphen")
    source = path.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    registry = load_json(
        settings.source_registry_path, {"schema": "pmem.sources.v1", "sources": []}
    )
    rows = registry.setdefault("sources", [])
    existing = next((row for row in rows if row.get("id") == source_id), None)
    payload = {"id": source_id, "path": str(source), "kind": kind}
    if existing is None:
        rows.append(payload)
    else:
        existing.update(payload)
    atomic_json(settings.source_registry_path, registry)


def _copy_segment(source: Path, destination: Path, offset: int, full: bool) -> None:
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    with source.open("rb") as src, temporary.open("wb") as dst:
        if not full:
            src.seek(offset)
        shutil.copyfileobj(src, dst)
    os.replace(temporary, destination)


def sync_archive(settings: Settings) -> dict:
    registry = load_json(
        settings.source_registry_path, {"schema": "pmem.sources.v1", "sources": []}
    )
    manifest = load_json(
        settings.manifest_path, {"schema": "pmem.archive.v1", "records": []}
    )
    records = manifest.setdefault("records", [])
    latest: dict[str, dict] = {}
    for row in records:
        source_id = row.get("source_id")
        if source_id:
            latest[source_id] = row

    stamp, captured_at = utc_stamp()
    additions: list[dict] = []
    target_dir = settings.archive_root / "sources"
    target_dir.mkdir(parents=True, exist_ok=True)
    for registered in registry.get("sources", []):
        source_id = str(registered["id"])
        source = Path(registered["path"])
        if not source.is_file():
            raise FileNotFoundError(f"registered source is missing: {source_id}: {source}")
        previous = latest.get(source_id)
        size = source.stat().st_size
        old_size = int(previous.get("source_bytes", 0)) if previous else 0
        if previous and size == old_size and sha256_file(source) == previous.get("source_sha256"):
            continue

        append_only = bool(
            previous
            and size > old_size
            and previous.get("source_sha256")
            and sha256_file(source, old_size) == previous.get("source_prefix_sha256")
        )
        mode = "append_delta" if append_only else "full_snapshot"
        suffix = source.suffix or ".bin"
        destination = target_dir / f"{source_id}.{mode}-{stamp}{suffix}"
        _copy_segment(source, destination, old_size, full=not append_only)
        source_hash = sha256_file(source)
        row = {
            "source_id": source_id,
            "kind": registered.get("kind", "generic"),
            "archive_path": str(destination.relative_to(settings.memory_root)),
            "capture_mode": mode,
            "source_offset_start": old_size if append_only else 0,
            "source_offset_end": size,
            "source_bytes": size,
            "bytes": destination.stat().st_size,
            "sha256": sha256_file(destination),
            "source_sha256": source_hash,
            "source_prefix_sha256": source_hash,
            "previous_archive_path": previous.get("archive_path") if previous else None,
            "previous_sha256": previous.get("sha256") if previous else None,
            "captured_at": captured_at,
        }
        if previous:
            previous["head"] = False
        row["head"] = True
        records.append(row)
        latest[source_id] = row
        additions.append(row)

    manifest["updated_at"] = captured_at
    atomic_json(settings.manifest_path, manifest)
    return {
        "added_records": len(additions),
        "added_bytes": sum(row["bytes"] for row in additions),
        "modes": {
            mode: sum(row["capture_mode"] == mode for row in additions)
            for mode in ("full_snapshot", "append_delta")
        },
    }


def archive_errors(settings: Settings, full_hash: bool) -> list[str]:
    errors: list[str] = []
    manifest = load_json(settings.manifest_path, {"records": []})
    by_path = {row.get("archive_path"): row for row in manifest.get("records", [])}
    seen: set[str] = set()
    for index, row in enumerate(manifest.get("records", []), 1):
        relative = row.get("archive_path")
        if not isinstance(relative, str) or relative in seen:
            errors.append(f"invalid or duplicate archive path at record {index}: {relative}")
            continue
        seen.add(relative)
        try:
            path = (settings.memory_root / relative).resolve()
            path.relative_to(settings.archive_root.resolve())
        except ValueError:
            errors.append(f"archive path escapes archive root: {relative}")
            continue
        if not path.is_file():
            errors.append(f"missing archive record: {relative}")
            continue
        if path.stat().st_size != row.get("bytes"):
            errors.append(f"archive size mismatch: {relative}")
        if full_hash and sha256_file(path) != row.get("sha256"):
            errors.append(f"archive hash mismatch: {relative}")
        previous_path = row.get("previous_archive_path")
        if previous_path:
            previous = by_path.get(previous_path)
            if previous is None:
                errors.append(f"broken archive ancestry: {relative} -> {previous_path}")
            elif previous.get("sha256") != row.get("previous_sha256"):
                errors.append(f"archive ancestry hash mismatch: {relative} -> {previous_path}")
            elif (
                row.get("capture_mode") == "append_delta"
                and row.get("source_offset_start") != previous.get("source_offset_end")
            ):
                errors.append(f"archive delta offset discontinuity: {relative}")
    return errors
