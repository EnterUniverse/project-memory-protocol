from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from project_memory_protocol.archive import archive_errors, register_source, sync_archive
from project_memory_protocol.audit import audit
from project_memory_protocol.claims import add_claim, validate_claims
from project_memory_protocol.config import load_settings
from project_memory_protocol.context import compile_context
from project_memory_protocol.drill import run_drill
from project_memory_protocol.indexer import build_index, retrieve
from project_memory_protocol.privacy import scan
from project_memory_protocol.templates import initialize


def settings_for(tmp_path: Path):
    initialize(tmp_path)
    return load_settings(tmp_path)


def test_init_is_idempotent_and_private_stores_are_ignored(tmp_path: Path):
    first = initialize(tmp_path)
    second = initialize(tmp_path)
    assert first
    assert second == []
    ignore = (tmp_path / ".project-memory" / ".gitignore").read_text()
    assert "archive/" in ignore
    assert "source_registry.json" in ignore
    assert (tmp_path / ".project-memory" / "RECOVERY.md").is_file()


def test_archive_uses_full_then_append_delta(tmp_path: Path):
    settings = settings_for(tmp_path)
    source = tmp_path / "conversation.jsonl"
    source.write_text('{"role":"user","content":"first"}\n')
    register_source(settings, "session-a", source, "generic-jsonl")
    first = sync_archive(settings)
    assert first["modes"]["full_snapshot"] == 1

    with source.open("a") as stream:
        stream.write('{"role":"assistant","content":"second"}\n')
    second = sync_archive(settings)
    assert second["modes"]["append_delta"] == 1
    assert archive_errors(settings, full_hash=True) == []

    manifest = json.loads(settings.manifest_path.read_text())
    assert len(manifest["records"]) == 2
    assert manifest["records"][1]["previous_sha256"] == manifest["records"][0]["sha256"]


def test_changed_prefix_creates_new_full_snapshot(tmp_path: Path):
    settings = settings_for(tmp_path)
    source = tmp_path / "source.jsonl"
    source.write_text('{"content":"first"}\n')
    register_source(settings, "source", source, "generic-jsonl")
    sync_archive(settings)
    source.write_text('{"content":"rewritten and longer"}\n')
    result = sync_archive(settings)
    assert result["modes"]["full_snapshot"] == 1


def test_index_and_retrieve_curated_and_archive_evidence(tmp_path: Path):
    settings = settings_for(tmp_path)
    (settings.memory_root / "CURRENT.md").write_text(
        "# Current state\n\nThe cobalt parser fails on compound labels.\n"
    )
    source = tmp_path / "evidence.jsonl"
    source.write_text('{"role":"user","content":"cobalt evidence from the source"}\n')
    register_source(settings, "evidence", source, "generic-jsonl")
    sync_archive(settings)
    result = build_index(settings, include_archive=True)
    assert result["chunks"] > 0
    rows = retrieve(settings, "cobalt")
    assert any("CURRENT.md" in row["source"] for row in rows)
    assert any(row["tier"] == "archive" for row in rows)


def test_context_pack_lists_omitted_retrievable_evidence(tmp_path: Path):
    settings = settings_for(tmp_path)
    for index in range(15):
        path = settings.memory_root / "modules" / f"module-{index}.md"
        path.write_text(f"# Module {index}\n\nquartz " + "evidence " * 200)
    build_index(settings)
    rendered = compile_context(settings, "orient", "quartz", None, token_budget=50)
    metadata_text = rendered.split("\n\n", 2)[1]
    metadata = json.loads(metadata_text)
    assert metadata["omitted_retrievable"]
    assert {row["reason"] for row in metadata["omitted_retrievable"]} <= {
        "token_budget",
        "tier_quota",
    }


def test_full_profile_ignores_budget_for_curated_sources(tmp_path: Path):
    settings = settings_for(tmp_path)
    stage = settings.memory_root / "stages" / "S001_BASELINE.md"
    stage.write_text("# S001 Baseline\n\n" + "evidence " * 400)
    rendered = compile_context(settings, "full", None, None, token_budget=1)
    metadata = json.loads(rendered.split("\n\n", 2)[1])
    sources = {row["source"] for row in metadata["selected"]}
    assert "stages/S001_BASELINE.md" in sources
    assert metadata["budget_exceeded_by_mandatory_core"] > 0


def test_claim_validation_requires_evidence_for_verified_claims(tmp_path: Path):
    settings = settings_for(tmp_path)
    with pytest.raises(ValueError):
        add_claim(settings, "verified", "A result exists.", [])
    row = add_claim(settings, "hypothesis", "The parser may need normalization.", [])
    assert row["id"] == "C0001"
    assert validate_claims(settings) == []


def test_claim_rejects_empty_text_and_invalid_dates(tmp_path: Path):
    settings = settings_for(tmp_path)
    with pytest.raises(ValueError, match="must not be empty"):
        add_claim(settings, "hypothesis", "   ", [])
    with pytest.raises(ValueError, match="invalid verification date"):
        add_claim(settings, "hypothesis", "A testable idea.", [], verified_at="2026-99-99")
    assert validate_claims(settings) == []


def test_privacy_scanner_supports_builtin_rules_and_private_blocklist(tmp_path: Path):
    tree = tmp_path / "release"
    tree.mkdir()
    private_email = "researcher" + "@example.org"
    (tree / "note.md").write_text(f"Contact {private_email} about ORCHID-CODENAME.\n")
    blocklist = tmp_path / "private-patterns.txt"
    blocklist.write_text("ORCHID-CODENAME\n")
    findings = scan(tree, blocklist)
    assert {finding.rule for finding in findings} == {"email", "private-blocklist"}
    assert all(private_email not in finding.excerpt for finding in findings)
    assert all("ORCHID-CODENAME" not in finding.excerpt for finding in findings)


def test_privacy_scanner_does_not_follow_symlinks(tmp_path: Path):
    outside = tmp_path / "outside.txt"
    fake_token = "ghp_" + "abcdefghijklmnopqrstuvwxyz1234567890"
    outside.write_text(f"token = {fake_token}\n")
    tree = tmp_path / "release"
    tree.mkdir()
    (tree / "linked.txt").symlink_to(outside)
    assert scan(tree) == []


def test_duplicate_text_keeps_each_source_locator(tmp_path: Path):
    settings = settings_for(tmp_path)
    repeated = "# Shared finding\n\nThe indigo result was reproduced.\n"
    (settings.memory_root / "modules" / "first.md").write_text(repeated)
    (settings.memory_root / "modules" / "second.md").write_text(repeated)
    build_index(settings)
    sources = {row["source"] for row in retrieve(settings, "indigo reproduced")}
    assert {"modules/first.md", "modules/second.md"} <= sources


def test_memory_directory_cannot_escape_project(tmp_path: Path):
    initialize(tmp_path)
    config = tmp_path / ".project-memory.toml"
    config.write_text(
        config.read_text().replace('directory = ".project-memory"', 'directory = "../private"')
    )
    with pytest.raises(ValueError, match="inside the project root"):
        load_settings(tmp_path)


def test_profile_paths_must_be_arrays(tmp_path: Path):
    initialize(tmp_path)
    config = tmp_path / ".project-memory.toml"
    config.write_text(
        config.read_text().replace(
            'orient = ["RECOVERY.md", "WORKING_SET.md"]', 'orient = "RECOVERY.md"'
        )
    )
    with pytest.raises(TypeError, match="profiles.orient"):
        load_settings(tmp_path)


def test_context_budget_must_be_positive(tmp_path: Path):
    settings = settings_for(tmp_path)
    with pytest.raises(ValueError, match="must be positive"):
        compile_context(settings, "orient", None, None, token_budget=0)


def test_recovery_drill_reports_invalid_probe_files(tmp_path: Path):
    settings = settings_for(tmp_path)
    (settings.memory_root / "recovery_probes.json").write_text('{"probes":[{}]}')
    with pytest.raises(ValueError, match="non-empty query"):
        run_drill(settings)


def test_privacy_scan_requires_an_existing_path(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        scan(tmp_path / "missing")


def test_recovery_drill_is_project_defined(tmp_path: Path):
    settings = settings_for(tmp_path)
    (settings.memory_root / "CURRENT.md").write_text(
        "# Current state\n\nThe amber tokenizer is the active baseline.\n"
    )
    probes = {
        "schema": "pmem.probes.v1",
        "probes": [
            {
                "name": "active baseline",
                "query": "amber tokenizer",
                "require_all": ["active baseline"],
            }
        ],
    }
    (settings.memory_root / "recovery_probes.json").write_text(json.dumps(probes))
    build_index(settings)
    result = run_drill(settings)
    assert result["status"] == "passed"
    assert len(result["probes"][0]["top_sources"]) == len(set(result["probes"][0]["top_sources"]))


def test_audit_detects_archive_tampering(tmp_path: Path):
    settings = settings_for(tmp_path)
    source = tmp_path / "source.jsonl"
    source.write_text('{"content":"evidence"}\n')
    register_source(settings, "source", source, "generic-jsonl")
    sync_archive(settings)
    manifest = json.loads(settings.manifest_path.read_text())
    archived = settings.memory_root / manifest["records"][0]["archive_path"]
    archived.write_text("tampered")
    result = audit(settings, full_hash=True)
    assert result["status"] == "invalid"
    assert any("archive" in error for error in result["errors"])


def test_sqlite_has_fts5_support():
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE VIRTUAL TABLE test USING fts5(text)")
    connection.close()
