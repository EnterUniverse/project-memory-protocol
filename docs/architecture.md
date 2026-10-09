# Architecture

## Separation of concerns

PMP separates four operations that are often conflated:

1. **Preservation** copies explicitly registered evidence into an immutable hash-linked archive.
2. **Interpretation** maintains human-readable current state, topic modules, decisions, and stages.
3. **Retrieval** builds a disposable lexical index and compiles question-scoped context packs.
4. **Verification** checks structure, archive integrity, privacy indicators, and recovery behavior.

No derived operation mutates the source archive.

## Archive ancestry

For each registered source, the first capture is a full snapshot. If the next source is an
append-only extension whose old prefix hash still matches, PMP stores only the new suffix. If the
prefix changed, PMP stores another full snapshot. Each record links to the previous archive path
and hash.

This establishes byte-level ancestry without claiming that the source itself was complete or
authentic.

## Retrieval

Markdown is chunked by heading. JSONL archive records are extracted as bounded text chunks.
SQLite FTS5 ranks matches, with a small authority prior for curated material and claims.

Context compilation begins with mandatory profile files, adds topic routes and query results,
then applies a token estimate and per-tier quotas. Every omitted result remains in metadata with a
source locator and omission reason. The `full` profile does not drop curated files for budget.

## Portability

Core state uses Markdown, JSON, JSONL, TOML, SHA-256, and SQLite. Provider-specific transcript
adapters can improve extraction, but the archive and generic JSON traversal do not require one.

