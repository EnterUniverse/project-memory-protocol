# Design

## Responsibilities

`pmem` keeps four jobs separate:

1. **Preservation** copies explicitly registered sources into a hash-linked archive.
2. **Project notes** keep current state, decisions, topics, and completed work readable.
3. **Retrieval** builds a disposable search index and assembles task-specific context.
4. **Checks** validate structure, archive integrity, privacy findings, and retrieval behavior.

No derived operation mutates the source archive.

## Archive ancestry

For each registered source, the first capture is a full snapshot. If the next source is an
append-only extension whose old prefix hash still matches, PMP stores only the new suffix. If the
prefix changed, PMP stores another full snapshot. Each record links to the previous archive path
and hash.

This records the byte-level history of captured files. It does not establish whether a source was
complete or trustworthy.

## Retrieval

Markdown is chunked by heading. JSONL archive records are extracted as bounded text chunks.
SQLite FTS5 ranks matches, with maintained project notes and claims ranked ahead of raw archives.

Context compilation begins with mandatory profile files, adds topic routes and query results,
then applies a token estimate and per-tier quotas. Every omitted result remains in metadata with a
source locator and omission reason. The `full` profile does not drop curated files for budget.

## Portability

Core state uses Markdown, JSON, JSONL, TOML, SHA-256, and SQLite. The archive does not depend on a
particular model provider or conversation format.
