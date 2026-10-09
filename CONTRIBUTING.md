# Contributing

Small, focused changes are easier to review and maintain. Before writing a large change, open an
issue that describes the user-visible problem and a minimal example.

Before submitting a change:

```bash
python -m pytest
ruff check .
ruff format --check .
pmem privacy scan .
```

Changes to archiving, ranking, context budgets, claims, or audits should include a regression test
or recovery probe that demonstrates the failure being addressed. Use synthetic data in issues,
tests, and examples; never include private conversations, machine paths, or credentials.

In a pull request, explain the behavior before and after the change, the trade-offs, and how you
verified it. Keep new dependencies and file formats justified by a concrete use case.
