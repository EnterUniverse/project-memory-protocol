from __future__ import annotations

import json

from .config import Settings
from .indexer import retrieve


def run_drill(settings: Settings) -> dict:
    probe_path = settings.memory_root / "recovery_probes.json"
    payload = json.loads(probe_path.read_text(encoding="utf-8"))
    outcomes = []
    for probe in payload.get("probes", []):
        rows = retrieve(settings, probe["query"], limit=int(probe.get("limit", 40)))
        haystack = "\n".join(
            f"{row['source']} {row['locator']} {row['text']}" for row in rows
        ).casefold()
        required = [str(term).casefold() for term in probe.get("require_all", [])]
        alternatives = [str(term).casefold() for term in probe.get("require_any", [])]
        passed = all(term in haystack for term in required) and (
            not alternatives or any(term in haystack for term in alternatives)
        )
        outcomes.append(
            {
                "name": probe.get("name", probe["query"]),
                "passed": passed,
                "top_sources": [row["source"] for row in rows[:5]],
            }
        )
    return {
        "status": "passed" if all(row["passed"] for row in outcomes) else "failed",
        "probes": outcomes,
    }

