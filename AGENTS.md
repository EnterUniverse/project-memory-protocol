# Agent development instructions

This is the public Project Memory Protocol repository. Use synthetic evidence only. Never add real
transcripts, personal identifiers, private project names, credentials, or machine-specific paths.

Preserve the distinction between immutable evidence, curated interpretation, typed claims,
disposable retrieval indexes, and live implementation truth. A context budget may omit derived
retrieval results but must expose their locators; it may not delete canonical evidence. The full
profile must retain every curated source.

Keep the core dependency-light and provider neutral. New infrastructure should address a measured
recovery, integrity, portability, or privacy failure. Changes to memory semantics require tests and,
when appropriate, a recovery probe.

Before handoff run:

```bash
pytest
ruff check .
pmem privacy scan .
python -m build
python -m twine check dist/*
```

