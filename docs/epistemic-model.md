# Epistemic model

PMP uses explicit claim states because “remembered” is not a sufficient epistemic category.

| Status | Meaning |
|---|---|
| `verified` | Supported by cited evidence within a stated scope |
| `user_constraint` | An explicit requirement that remains binding until superseded |
| `interpretation` | A reasoned reading of evidence, open to revision |
| `hypothesis` | A proposition that still requires testing |
| `rejected` | A tested or reasoned route that was not accepted within its recorded boundary |
| `superseded` | A former claim replaced by a later claim without deleting its history |

Verification is scoped. A passing unit test does not verify deployment state; a transcript does not
verify implementation; a paper does not prove that local code implements the paper.

The system therefore keeps three authorities separate:

- source evidence establishes what was observed, requested, or recorded;
- curated memory establishes the current interpretation and navigation map;
- live project evidence establishes present implementation and volatile status.

This separation is intended to reduce two opposing failures: forgetting causal history and becoming
anchored to an obsolete historical conclusion.

