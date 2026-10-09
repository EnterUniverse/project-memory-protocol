from __future__ import annotations

import json
from pathlib import Path

from .config import Settings, expand_memory_paths
from .indexer import retrieve
from .util import estimated_tokens, sha256_file


def render_files(settings: Settings, paths: list[Path]) -> list[dict]:
    output: list[dict] = []
    for path in paths:
        if path.is_file():
            output.append(
                {
                    "source": str(path.relative_to(settings.memory_root)),
                    "locator": "complete-file",
                    "tier": "core",
                    "authority": 100,
                    "source_sha256": sha256_file(path),
                    "text": path.read_text(encoding="utf-8").rstrip(),
                }
            )
    return output


def profile_paths(settings: Settings, profile: str, topic: str | None) -> list[Path]:
    if profile == "orient":
        paths = expand_memory_paths(settings, settings.orient)
    elif profile == "startup":
        paths = expand_memory_paths(settings, settings.startup)
    elif profile == "full":
        paths = expand_memory_paths(settings, settings.startup + settings.full_extra)
    else:
        raise ValueError(f"unknown profile: {profile}")
    if topic:
        try:
            topic_path = settings.memory_root / settings.topics[topic]
        except KeyError as error:
            raise ValueError(f"unknown topic: {topic}") from error
        if topic_path.is_file():
            paths.append(topic_path)
    return list(dict.fromkeys(paths))


def compile_context(
    settings: Settings,
    profile: str,
    query: str | None,
    topic: str | None,
    token_budget: int | None,
) -> str:
    budget = token_budget or settings.default_budget
    mandatory = profile_paths(settings, profile, topic)
    candidates = render_files(settings, mandatory)
    if query:
        candidates.extend(retrieve(settings, query))

    complete_sources = {
        row["source"] for row in candidates if row["locator"] == "complete-file"
    }
    mandatory_sources = {str(path.relative_to(settings.memory_root)) for path in mandatory}
    selected: list[dict] = []
    omitted: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    used = 0
    mandatory_used = 0
    tier_counts: dict[str, int] = {}
    quotas = {"claim": 8, "curated": 8, "stage": 8, "archive": 6}

    for row in candidates:
        if row["source"] in complete_sources and row["locator"] != "complete-file":
            continue
        key = (row["source"], row["locator"], row["source_sha256"])
        if key in seen:
            continue
        seen.add(key)
        cost = estimated_tokens(row["text"])
        is_mandatory = row["source"] in mandatory_sources
        tier = row.get("tier", "curated")
        if not is_mandatory and tier_counts.get(tier, 0) >= quotas.get(tier, 10_000):
            omitted.append(
                {
                    "source": row["source"],
                    "locator": row["locator"],
                    "estimated_tokens": cost,
                    "reason": "tier_quota",
                }
            )
            continue
        if is_mandatory or used + cost <= budget:
            selected.append(row)
            used += cost
            mandatory_used += cost if is_mandatory else 0
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        else:
            omitted.append(
                {
                    "source": row["source"],
                    "locator": row["locator"],
                    "estimated_tokens": cost,
                    "reason": "token_budget",
                }
            )

    metadata = {
        "schema": "pmem.context-pack.v1",
        "profile": profile,
        "topic": topic,
        "query": query,
        "estimated_tokens": used,
        "budget": budget,
        "epistemic_contract": "memory_is_evidence_not_a_preselected_answer",
        "budget_exceeded_by_mandatory_core": max(0, mandatory_used - budget),
        "selected": [
            {
                "source": row["source"],
                "locator": row["locator"],
                "sha256": row["source_sha256"],
            }
            for row in selected
        ],
        "omitted_retrievable": omitted,
    }
    sections = ["--- CONTEXT_PACK_METADATA ---", json.dumps(metadata, indent=2)]
    for row in selected:
        sections.extend(
            [
                f"--- {row['source']} :: {row['locator']} :: sha256={row['source_sha256']} ---",
                row["text"],
            ]
        )
    return "\n\n".join(sections) + "\n"
