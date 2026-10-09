# Contributing

PMP favors small, inspectable changes over opaque infrastructure.

Before submitting a change:

```bash
python -m pytest
ruff check .
pmem privacy scan .
```

Changes to preservation, ranking, context budgets, claim semantics, or audit behavior should include
a regression test or recovery probe that demonstrates the failure being addressed. Do not add real
conversation logs, personal paths, private project names, or credentials to issues or fixtures.

Please explain the epistemic effect of a change: what becomes easier to recover, what can now be
omitted, and which authority or failure mode is affected.

