# File format reference

## Project configuration

`.project-memory.toml` identifies the memory directory, recovery profiles, retrieval budget, and
stable topic routes. Paths are project-relative. Machine-specific source paths belong only in the
ignored `source_registry.json`.

## Archive manifest

Each archive record contains:

- `source_id` and evidence `kind`;
- project-memory-relative `archive_path`;
- `full_snapshot` or `append_delta` capture mode;
- source byte offsets and total byte length;
- SHA-256 of the archived file and complete source state;
- previous archive path and hash;
- UTC capture timestamp.

The manifest can detect later changes to captured bytes and records their ancestry. It does not
prove that the original source was complete or trustworthy.

## Claims

`claims/CLAIMS.jsonl` contains one JSON object per atomic claim:

```json
{
  "id": "C0001",
  "status": "hypothesis",
  "claim": "Normalization may be responsible for the mismatch.",
  "evidence": ["CURRENT.md#normalization"],
  "verified_at": "2026-01-15",
  "supersedes": [],
  "superseded_by": []
}
```

IDs are stable. Supersession links are symmetric. `verified` and `user_constraint` claims require
evidence. The date records when the claim status was last justified, not necessarily when the
underlying event happened.

## Context packs

A context pack begins with `pmem.context-pack.v1` metadata. `selected` records source locators and
hashes. `omitted_retrievable` records candidates excluded by token budget or tier quota. Consumers
should retain this metadata when passing the text between agents.
