# Claim states

An item appearing in project memory does not make it true. Claims can therefore carry one of these
states:

| Status | Meaning |
|---|---|
| `verified` | Supported by cited evidence within a stated scope |
| `user_constraint` | An explicit requirement that remains binding until superseded |
| `interpretation` | A reasoned reading of evidence, open to revision |
| `hypothesis` | A proposition that still requires testing |
| `rejected` | A tested or reasoned route that was not accepted within its recorded boundary |
| `superseded` | A former claim replaced by a later claim without deleting its history |

Verification has a scope. A passing unit test does not verify deployment state; a conversation does not
verify implementation; a paper does not prove that local code implements the paper.

The system therefore keeps three authorities separate:

- source evidence establishes what was observed, requested, or recorded;
- curated memory establishes the current interpretation and navigation map;
- live project evidence establishes present implementation and volatile status.

Keeping these roles separate helps preserve useful history without treating an old conclusion as
current fact.
