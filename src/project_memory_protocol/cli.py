from __future__ import annotations

import argparse
import json
import sys
from importlib.metadata import version
from pathlib import Path

from .archive import register_source, sync_archive
from .audit import audit
from .claims import VALID_STATUSES, add_claim
from .config import load_settings
from .context import compile_context
from .drill import run_drill
from .indexer import build_index
from .privacy import scan
from .templates import initialize


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="pmem", description="Keep project context across AI-assisted work."
    )
    root.add_argument("--version", action="version", version=version("project-memory-protocol"))
    commands = root.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="initialize memory files in a project")
    init.add_argument("path", nargs="?", default=".")

    source = commands.add_parser("source", help="manage explicit private evidence sources")
    source_commands = source.add_subparsers(dest="source_command", required=True)
    source_add = source_commands.add_parser("add")
    source_add.add_argument("path")
    source_add.add_argument("--id", required=True)
    source_add.add_argument("--kind", default="generic-jsonl")

    archive = commands.add_parser("archive", help="synchronize registered evidence")
    archive_commands = archive.add_subparsers(dest="archive_command", required=True)
    archive_commands.add_parser("sync")

    index = commands.add_parser("index", help="rebuild the disposable FTS index")
    index.add_argument("--include-archive", action="store_true")

    compile_command = commands.add_parser("compile", help="compile a context pack")
    compile_command.add_argument(
        "--profile", choices=("orient", "startup", "full"), default="orient"
    )
    compile_command.add_argument("--topic")
    compile_command.add_argument("--query")
    compile_command.add_argument("--token-budget", type=int)
    compile_command.add_argument("--output")

    claim = commands.add_parser("claim", help="append an atomic claim")
    claim_commands = claim.add_subparsers(dest="claim_command", required=True)
    claim_add = claim_commands.add_parser("add")
    claim_add.add_argument("--status", choices=sorted(VALID_STATUSES), required=True)
    claim_add.add_argument("--claim", required=True)
    claim_add.add_argument("--evidence", action="append", default=[])
    claim_add.add_argument("--verified-at")

    audit_command = commands.add_parser("audit", help="validate memory integrity")
    audit_command.add_argument("--full-hash", action="store_true")
    audit_command.add_argument("--privacy-root")
    audit_command.add_argument("--blocklist")

    privacy = commands.add_parser("privacy", help="scan a tree for likely private material")
    privacy_commands = privacy.add_subparsers(dest="privacy_command", required=True)
    privacy_scan = privacy_commands.add_parser("scan")
    privacy_scan.add_argument("path", nargs="?", default=".")
    privacy_scan.add_argument("--blocklist")

    commands.add_parser("drill", help="run configured retrieval regression probes")
    return root


def emit(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "init":
            created = initialize(Path(args.path).resolve())
            emit({"created": [str(path) for path in created]})
            return 0
        if args.command == "privacy" and args.privacy_command == "scan":
            findings = scan(
                Path(args.path), Path(args.blocklist).resolve() if args.blocklist else None
            )
            emit([finding.__dict__ for finding in findings])
            return 1 if findings else 0

        settings = load_settings()
        if args.command == "source" and args.source_command == "add":
            register_source(settings, args.id, Path(args.path), args.kind)
            emit({"registered": args.id})
            return 0
        if args.command == "archive" and args.archive_command == "sync":
            emit(sync_archive(settings))
            return 0
        if args.command == "index":
            emit(build_index(settings, include_archive=args.include_archive))
            return 0
        if args.command == "compile":
            rendered = compile_context(
                settings, args.profile, args.query, args.topic, args.token_budget
            )
            if args.output:
                Path(args.output).write_text(rendered, encoding="utf-8")
            else:
                print(rendered, end="")
            return 0
        if args.command == "claim" and args.claim_command == "add":
            emit(
                add_claim(
                    settings,
                    args.status,
                    args.claim,
                    args.evidence,
                    args.verified_at,
                )
            )
            return 0
        if args.command == "audit":
            result = audit(
                settings,
                full_hash=args.full_hash,
                privacy_root=Path(args.privacy_root).resolve() if args.privacy_root else None,
                blocklist=Path(args.blocklist).resolve() if args.blocklist else None,
            )
            emit(result)
            return 0 if result["status"] == "valid" else 1
        if args.command == "drill":
            result = run_drill(settings)
            emit(result)
            return 0 if result["status"] == "passed" else 1
    except (OSError, TypeError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"pmem: {error}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
