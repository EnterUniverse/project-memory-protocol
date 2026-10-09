# Project Memory Protocol

[![CI](https://github.com/EnterUniverse/project-memory-protocol/actions/workflows/ci.yml/badge.svg)](https://github.com/EnterUniverse/project-memory-protocol/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)

[简体中文](README.zh-CN.md)

Local project memory for AI-assisted work.

Project Memory Protocol (`pmem`) is a command-line tool for carrying useful context across coding
and research sessions. It keeps working state in readable files, preserves only the evidence
sources you choose, and assembles a focused context pack when a new session begins.

Everything runs locally. The core has no model API, hosted service, or runtime dependency outside
the Python standard library.

## Quick start

Requires Python 3.11 or later.

```bash
python -m pip install git+https://github.com/EnterUniverse/project-memory-protocol.git@v0.1.0
cd your-project
pmem init
```

`pmem init` creates a `.project-memory/` directory. Start by editing two files:

- `WORKING_SET.md` — a short map for someone entering the project;
- `CURRENT.md` — the state and reasoning that should survive the current session.

Then build the local index and retrieve context for a task:

```bash
pmem index
pmem compile --query "Why did we change the storage format?"
```

The result is Markdown that can be read directly or passed to an AI agent. It includes source
locations and records relevant items omitted by the token budget.

## What it keeps

```text
.project-memory/
├── RECOVERY.md             # how a new session should begin
├── WORKING_SET.md          # short orientation
├── CURRENT.md              # active state and reasoning
├── OPEN_LOOPS.md           # unfinished work and commitments
├── DECISIONS.md            # decisions and rationale
├── PROJECT_NARRATIVE.md    # longer project history
├── claims/CLAIMS.jsonl     # individual claims and evidence links
├── modules/                # topic-specific notes
└── stages/                 # completed iterations
```

These files are ordinary Markdown and JSONL, so they remain useful without `pmem`. Generated
indexes, machine-specific source paths, and raw archives are ignored by Git by default.

## Adding source material

Curated notes are often enough. To preserve a conversation, tool trace, or other append-only JSONL
file, register it explicitly:

```bash
pmem source add path/to/conversation.jsonl --id design-session --kind generic-jsonl
pmem archive sync
pmem index --include-archive
```

The first sync stores a full snapshot. Later append-only changes are stored as deltas; a changed
prefix starts a new snapshot. Archive records carry SHA-256 hashes and ancestry links.

`pmem` never searches your home directory for conversations or uploads project data.

## Workflow

```text
maintained notes ───────────────┐
                               ├─> local index ─> task context
registered sources ─> archive ─┘
          │                          │
          └──────── integrity and recovery checks
```

A typical handoff looks like this:

```bash
# Preserve newly appended source material, if any
pmem archive sync

# Refresh retrieval and compile context for the next task
pmem index --include-archive
pmem compile --query "What remains unresolved in the import pipeline?" --token-budget 8000

# Check archive hashes, file structure, claims, and privacy findings
pmem audit --full-hash
```

For broader recovery, use `--profile orient`, `--profile startup`, or `--profile full`. Projects can
also keep realistic retrieval questions in `.project-memory/recovery_probes.json` and run them with
`pmem drill`.

## Commands

| Command | Purpose |
|---|---|
| `pmem init` | Create the project-memory files |
| `pmem source add` | Register a local evidence source |
| `pmem archive sync` | Snapshot or append new source material |
| `pmem index` | Rebuild the local SQLite FTS index |
| `pmem compile` | Build a context pack for a query or profile |
| `pmem claim add` | Record a claim with status and evidence |
| `pmem audit` | Check structure and archive integrity |
| `pmem privacy scan` | Find common secrets and personal identifiers |
| `pmem drill` | Run retrieval regression checks |

Run `pmem <command> --help` for command options.

## Design boundaries

Project memory is a navigation layer, not an authority over the project. Current code, data,
artifacts, processes, and logs still need to be checked when they can change.

The tool deliberately separates source material from maintained notes, current state from completed
history, claims from their supporting evidence, and durable files from disposable search indexes.
This makes it possible to update an interpretation without deleting the record that led to it.
See [Design](docs/architecture.md) for details.

## Documentation

- [Documentation index](docs/README.md)
- [Using `pmem` with an AI agent](docs/agent-integration.md)
- [Design and storage model](docs/architecture.md)
- [File formats and context-pack reference](docs/schema.md)
- [Privacy and limitations](docs/threat-model.md)
- [Claim states](docs/epistemic-model.md)
- [Recovery checks](docs/evaluation.md)
- [Release procedure](docs/releasing.md)

## Project status

The current release is an early, usable implementation. File formats are plain and inspectable;
CLI and schema details may change before 1.0. Feedback based on real recovery failures is
particularly useful.

## Development

```bash
git clone https://github.com/EnterUniverse/project-memory-protocol.git
cd project-memory-protocol
python -m pip install -e ".[dev]"
pytest
ruff check .
ruff format --check .
```

See [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a change.

## License

Apache-2.0. See [LICENSE](LICENSE).
