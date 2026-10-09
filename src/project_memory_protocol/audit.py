from __future__ import annotations

import json
from pathlib import Path

from .archive import archive_errors
from .claims import validate_claims
from .config import Settings, expand_memory_paths
from .privacy import scan


def audit(
    settings: Settings,
    full_hash: bool = False,
    privacy_root: Path | None = None,
    blocklist: Path | None = None,
) -> dict:
    errors: list[str] = []
    required = expand_memory_paths(settings, settings.orient + settings.startup)
    required_names = set(settings.orient + settings.startup)
    found_names = {str(path.relative_to(settings.memory_root)) for path in required}
    for missing in sorted(required_names - found_names):
        errors.append(f"missing required memory file: {missing}")
    errors.extend(validate_claims(settings))
    errors.extend(archive_errors(settings, full_hash=full_hash))

    privacy_findings = []
    if privacy_root is not None:
        privacy_findings = [finding.__dict__ for finding in scan(privacy_root, blocklist)]
        errors.extend(
            f"privacy finding {row['rule']}: {row['path']}:{row['line']}"
            for row in privacy_findings
        )
    manifest = json.loads(settings.manifest_path.read_text(encoding="utf-8"))
    return {
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "archive_records": len(manifest.get("records", [])),
        "privacy_findings": privacy_findings,
        "full_hash": full_hash,
    }
