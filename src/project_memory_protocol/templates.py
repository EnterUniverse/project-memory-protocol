from __future__ import annotations

import json
from pathlib import Path

CONFIG = """[memory]
directory = ".project-memory"

[profiles]
orient = ["RECOVERY.md", "WORKING_SET.md"]
startup = ["RECOVERY.md", "WORKING_SET.md", "CURRENT.md", "OPEN_LOOPS.md", "DECISIONS.md"]
full_extra = ["PROJECT_NARRATIVE.md", "TIMELINE.md", "PATHS.md", "SOURCES.md", "ARCHIVE_INDEX.md", "claims/CLAIMS.jsonl", "modules/*.md", "stages/*.md"]

[retrieval]
default_token_budget = 12000

[topics]
# Add stable routes, for example:
# data = "modules/DATA.md"
"""


FILES = {
    "RECOVERY.md": """# Recovery

1. Read `WORKING_SET.md` for a short project map.
2. Read `CURRENT.md` and `OPEN_LOOPS.md` when the task depends on recent work.
3. Use `pmem compile --query "..."` to find context for the actual question.
4. Check current code, data, artifacts, and logs before relying on an old result.
5. Update the relevant files before ending a session.
""",
    "WORKING_SET.md": """# Working set

Keep this file short. It should be enough to enter the project and know where to look next.

## Objective

<!-- What is the project trying to achieve? -->

## Current status

<!-- What works, what is in progress, and what is blocked? -->

## Constraints

<!-- Record constraints that must survive across sessions. -->

## Project map

<!-- Point to the most useful files, modules, experiments, and evidence. -->
""",
    "CURRENT.md": """# Current state

## Active work

## Findings

## Uncertainty

## Next steps
""",
    "OPEN_LOOPS.md": """# Open loops

Track unfinished work that should survive the current session.

| Item | Status | Next action | Related context |
|---|---|---|---|
""",
    "PROJECT_NARRATIVE.md": """# Project narrative

Use this file when the short working set is no longer enough to explain how the project reached its
current shape. Link important statements to decisions, experiments, code, or source material.
""",
    "DECISIONS.md": """# Decisions

For each consequential decision, record the date, choice, reason, alternatives considered, and the
evidence or implementation that should be checked later.
""",
}


def initialize(root: Path) -> list[Path]:
    root.mkdir(parents=True, exist_ok=True)
    config = root / ".project-memory.toml"
    memory = root / ".project-memory"
    created: list[Path] = []
    if not config.exists():
        config.write_text(CONFIG, encoding="utf-8")
        created.append(config)
    for directory in ("archive", "claims", "index", "modules", "stages"):
        (memory / directory).mkdir(parents=True, exist_ok=True)
    for relative, content in FILES.items():
        destination = memory / relative
        if not destination.exists():
            destination.write_text(content, encoding="utf-8")
            created.append(destination)
    claims = memory / "claims" / "CLAIMS.jsonl"
    if not claims.exists():
        claims.write_text("", encoding="utf-8")
        created.append(claims)
    manifest = memory / "archive" / "manifest.json"
    if not manifest.exists():
        manifest.write_text(
            json.dumps({"schema": "pmem.archive.v1", "records": []}, indent=2) + "\n"
        )
        created.append(manifest)
    registry = memory / "source_registry.json"
    if not registry.exists():
        registry.write_text(
            json.dumps({"schema": "pmem.sources.v1", "sources": []}, indent=2) + "\n"
        )
        created.append(registry)
    ignore = memory / ".gitignore"
    if not ignore.exists():
        ignore.write_text(
            "archive/\nindex/\nsource_registry.json\nprivate-patterns.txt\n", encoding="utf-8"
        )
        created.append(ignore)
    probes = memory / "recovery_probes.json"
    if not probes.exists():
        probes.write_text(json.dumps({"schema": "pmem.probes.v1", "probes": []}, indent=2) + "\n")
        created.append(probes)
    return created
