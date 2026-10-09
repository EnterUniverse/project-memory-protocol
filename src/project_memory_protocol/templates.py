from __future__ import annotations

import json
from pathlib import Path

CONFIG = """[memory]
directory = ".project-memory"

[profiles]
orient = ["RECOVERY.md", "WORKING_SET.md"]
startup = ["START_HERE.md", "RECOVERY.md", "WORKING_SET.md", "CURRENT.md", "OPEN_LOOPS.md", "PROJECT_NARRATIVE.md"]
full_extra = ["DECISIONS.md", "TIMELINE.md", "PATHS.md", "SOURCES.md", "ARCHIVE_INDEX.md", "claims/CLAIMS.jsonl", "modules/*.md", "stages/*.md"]

[retrieval]
default_token_budget = 12000

[topics]
# Add stable routes, for example:
# data = "modules/DATA.md"
"""


FILES = {
    "RECOVERY.md": """# Recovery protocol

1. Read `WORKING_SET.md` for compact orientation.
2. Compile a question-scoped context pack for focused work.
3. Read relevant `CURRENT.md` and `OPEN_LOOPS.md` sections when status matters.
4. Inspect live code, artifacts, processes, and logs before implementation claims.
5. Treat memory as evidence and navigation, not as a preselected answer.
6. Preserve contradictions and distinguish constraints, facts, interpretations, and hypotheses.
""",
    "WORKING_SET.md": """# Working set

This compact file routes a fresh agent into the project. Record only the current boundary,
high-risk invariants, and pointers for deeper recovery. Do not turn it into a second narrative.

## Current boundary

- Replace this placeholder with the smallest accurate orientation.

## Expansion triggers

- Read `CURRENT.md` and `OPEN_LOOPS.md` for active or incomplete work.
- Read topic modules and evidence before substantive conclusions.
""",
    "START_HERE.md": """# Start here

Read `RECOVERY.md` and `WORKING_SET.md`. Use focused retrieval for the current question.
Use the startup or full profile only when the scope requires it.
""",
    "CURRENT.md": """# Current state

Record material active reasoning, uncertainty, evidence routes, and unfinished commitments.
Do not record transient progress percentages that belong in run logs.
""",
    "OPEN_LOOPS.md": """# Open loops

Record incomplete, paused, rejected, or promised work that must survive a phase change.
""",
    "PROJECT_NARRATIVE.md": """# Project narrative

Maintain the causal explanation of the project and its current implementation reality.
Link claims to evidence and preserve material supersession.
""",
    "DECISIONS.md": """# Decisions

Accepted, rejected, and superseded decisions belong here with rationale and evidence.
""",
    "TIMELINE.md": """# Timeline

This is an index of completed stages, not a replacement for stage cards.
""",
    "PATHS.md": """# Paths

Document stable project-relative locations. Avoid machine-specific absolute paths.
""",
    "SOURCES.md": """# Sources

Record authoritative external and internal evidence routes.
""",
    "ARCHIVE_INDEX.md": """# Archive index

The machine-readable archive manifest is authoritative. Summarize coverage and known gaps here.
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
        manifest.write_text(json.dumps({"schema": "pmem.archive.v1", "records": []}, indent=2) + "\n")
        created.append(manifest)
    registry = memory / "source_registry.json"
    if not registry.exists():
        registry.write_text(json.dumps({"schema": "pmem.sources.v1", "sources": []}, indent=2) + "\n")
        created.append(registry)
    ignore = memory / ".gitignore"
    if not ignore.exists():
        ignore.write_text("archive/\nindex/\nsource_registry.json\nprivate-patterns.txt\n", encoding="utf-8")
        created.append(ignore)
    probes = memory / "recovery_probes.json"
    if not probes.exists():
        probes.write_text(json.dumps({"schema": "pmem.probes.v1", "probes": []}, indent=2) + "\n")
        created.append(probes)
    return created
