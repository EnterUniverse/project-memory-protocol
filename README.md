# Project Memory Protocol

[![CI](https://github.com/EnterUniverse/project-memory-protocol/actions/workflows/ci.yml/badge.svg)](https://github.com/EnterUniverse/project-memory-protocol/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)

A small, local-first toolkit for keeping long-running AI-assisted projects coherent across
conversations.

I built this after repeatedly running into the same problem in research projects: a short summary
is convenient, but it gradually loses why decisions were made, which results were uncertain, what
failed, and where the original evidence lives. Saving every conversation solves the opposite
problem—you keep everything, but recovering the right context becomes difficult.

Project Memory Protocol keeps the durable parts in plain files, preserves source evidence
separately, and builds a focused context pack for the question at hand. It is intentionally simple:
Markdown, JSONL, SQLite FTS, SHA-256, and a Python CLI.

Created and maintained by [EnterUniverse](https://github.com/EnterUniverse).

> **Status:** v0.1 is usable for experimentation and personal projects. The file formats are
> inspectable, but the CLI may still change before 1.0.

## What it does

- Creates a readable project-memory layout instead of a single growing summary.
- Preserves explicitly registered conversations or other JSONL sources as hash-linked snapshots.
- Separates current state, open work, decisions, topic notes, completed stages, and atomic claims.
- Builds a local SQLite FTS index; no hosted service or model API is required.
- Compiles small, question-specific context packs and lists relevant material left out by budget.
- Validates archive integrity, claim structure, and project-defined recovery checks.
- Includes a privacy scanner for common secrets, personal paths, email addresses, and custom terms.

It does **not** decide what is true, replace inspection of current code and logs, or upload your
project memory anywhere.

## Quick start

PMP requires Python 3.11 or later. Install directly from GitHub:

```bash
python -m pip install git+https://github.com/EnterUniverse/project-memory-protocol.git
```

Initialize it inside a project:

```bash
cd your-project
pmem init
```

This creates `.project-memory/` with a small set of Markdown files:

```text
.project-memory/
├── WORKING_SET.md      # short orientation for a fresh conversation
├── CURRENT.md          # active reasoning and current state
├── OPEN_LOOPS.md       # unfinished, paused, or promised work
├── DECISIONS.md        # decisions and their rationale
├── PROJECT_NARRATIVE.md
├── claims/CLAIMS.jsonl
├── modules/
└── stages/
```

The raw archive, local search index, and source registry are ignored by Git by default.

To preserve a conversation or another append-only JSONL source:

```bash
pmem source add path/to/conversation.jsonl --id design-session --kind generic-jsonl
pmem archive sync
```

Build the index and recover context for a concrete question:

```bash
pmem index --include-archive
pmem compile --query "why was the storage format changed?" --token-budget 8000
```

For a broader restart or audit:

```bash
pmem compile --profile orient
pmem compile --profile startup
pmem compile --profile full > full-context.md
pmem audit --full-hash
```

Run `pmem --help` to see all commands.

## Why the files are separated

Different project records answer different questions:

| File or layer | What it is for |
|---|---|
| Source archive | What was actually recorded; immutable after capture |
| `WORKING_SET.md` | The shortest useful orientation for a fresh session |
| `CURRENT.md` | Material current reasoning, including uncertainty |
| `OPEN_LOOPS.md` | Work that must not disappear just because it is unfinished |
| `claims/CLAIMS.jsonl` | Small claims with status, evidence, and replacement links |
| `modules/` | Current understanding of individual topics |
| `stages/` | Completed iterations, including bounded negative results |
| Git and live artifacts | What the implementation currently is |

The important rule is that memory helps an agent find and interpret evidence; it does not become a
new source of truth for changing code, data, processes, or experimental results.

## Recovery checks

Search quality can regress as terminology and files change. PMP lets a project keep a few realistic
questions in `.project-memory/recovery_probes.json` and rerun them:

```bash
pmem drill
```

These are ordinary regression tests for project continuity: can a fresh session still find the
current goal, a critical constraint, the reason behind a decision, or a known failed route?

## Privacy

PMP never searches your home directory for conversations. A source is archived only after you
register it. Raw archives, source paths, and search indexes are private by default.

Before sharing a memory template or repository, run:

```bash
pmem privacy scan . --blocklist .project-memory/private-patterns.txt
```

The scanner catches common leaks but cannot prove that arbitrary prose is non-sensitive. Review the
Git history and release artifact as well. This repository itself was written as a clean public
implementation and contains only synthetic examples.

## Documentation

- [How the components fit together](docs/architecture.md)
- [Using PMP with coding or research agents](docs/agent-integration.md)
- [File and claim formats](docs/schema.md)
- [Privacy assumptions and release checks](docs/threat-model.md)
- [Why claims have explicit states](docs/epistemic-model.md)
- [Recovery evaluation](docs/evaluation.md)

## Development

```bash
git clone https://github.com/EnterUniverse/project-memory-protocol.git
cd project-memory-protocol
python -m pip install -e ".[dev]"
pytest
ruff check .
```

Contributions are welcome when they keep the system understandable and address a concrete recovery,
integrity, portability, or privacy problem. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache-2.0. See [LICENSE](LICENSE).
