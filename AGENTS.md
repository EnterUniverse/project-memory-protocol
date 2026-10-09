# Agent development instructions

This is the public Project Memory Protocol repository. Use synthetic evidence only. Never add real
transcripts, personal identifiers, private project names, credentials, or machine-specific paths.

Preserve source archives, keep maintained notes separate from raw material, and treat generated
indexes as disposable. A context budget may omit search results only when the output records what
was omitted. The full profile must retain every maintained project-memory file.

Keep the core dependency-light and provider neutral. New infrastructure should address a concrete
recovery, integrity, portability, or privacy problem. Behavior changes require tests and, when
appropriate, a recovery probe.

Before handoff run:

```bash
pytest
ruff check .
ruff format --check .
pmem privacy scan .
python -m build
python -m twine check dist/*
```
