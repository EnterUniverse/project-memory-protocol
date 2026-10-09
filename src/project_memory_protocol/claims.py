from __future__ import annotations

import json
import re
from datetime import UTC, date, datetime
from pathlib import Path

from .config import Settings

VALID_STATUSES = {
    "verified",
    "user_constraint",
    "interpretation",
    "hypothesis",
    "rejected",
    "superseded",
}


def load_claims(path: Path) -> tuple[list[dict], list[str]]:
    claims: list[dict] = []
    errors: list[str] = []
    if not path.is_file():
        return claims, [f"missing claims ledger: {path}"]
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as error:
            errors.append(f"invalid claim JSON line {line_number}: {error}")
            continue
        if not isinstance(value, dict):
            errors.append(f"claim line {line_number} is not an object")
            continue
        claims.append(value)
    return claims, errors


def validate_claims(settings: Settings) -> list[str]:
    claims, errors = load_claims(settings.claims_path)
    identifiers: set[str] = set()
    for row in claims:
        identifier = str(row.get("id", ""))
        if not re.fullmatch(r"C\d{4}", identifier):
            errors.append(f"invalid claim id: {identifier}")
        elif identifier in identifiers:
            errors.append(f"duplicate claim id: {identifier}")
        identifiers.add(identifier)
        if row.get("status") not in VALID_STATUSES:
            errors.append(f"invalid claim status {identifier}: {row.get('status')}")
        if not str(row.get("claim", "")).strip():
            errors.append(f"empty claim: {identifier}")
        evidence = row.get("evidence", [])
        if not isinstance(evidence, list):
            errors.append(f"claim {identifier} evidence must be a list")
            evidence = []
        if row.get("status") in {"verified", "user_constraint"} and not evidence:
            errors.append(f"claim lacks evidence: {identifier}")
        try:
            date.fromisoformat(str(row.get("verified_at", "")))
        except ValueError:
            errors.append(f"invalid verification date: {identifier}")
        for field in ("supersedes", "superseded_by"):
            if not isinstance(row.get(field, []), list):
                errors.append(f"claim {identifier} has non-list {field}")

    by_id = {str(row.get("id")): row for row in claims}
    for row in claims:
        identifier = str(row.get("id"))
        for previous in row.get("supersedes", []):
            if previous not in by_id:
                errors.append(f"claim {identifier} supersedes unknown {previous}")
            elif identifier not in by_id[previous].get("superseded_by", []):
                errors.append(f"asymmetric supersession: {identifier} -> {previous}")
        for later in row.get("superseded_by", []):
            if later not in by_id:
                errors.append(f"claim {identifier} superseded by unknown {later}")
            elif identifier not in by_id[later].get("supersedes", []):
                errors.append(f"asymmetric supersession: {identifier} <- {later}")
    return errors


def add_claim(
    settings: Settings,
    status: str,
    claim: str,
    evidence: list[str],
    verified_at: str | None = None,
) -> dict:
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status: {status}")
    if not claim.strip():
        raise ValueError("claim must not be empty")
    if status in {"verified", "user_constraint"} and not evidence:
        raise ValueError(f"{status} claims require evidence")
    verification_date = verified_at or datetime.now(UTC).date().isoformat()
    try:
        date.fromisoformat(verification_date)
    except ValueError as error:
        raise ValueError(f"invalid verification date: {verification_date}") from error
    claims, errors = load_claims(settings.claims_path)
    errors.extend(validate_claims(settings))
    if errors:
        raise ValueError("claims ledger is invalid: " + "; ".join(dict.fromkeys(errors)))
    highest = max((int(str(row["id"])[1:]) for row in claims), default=0)
    row = {
        "id": f"C{highest + 1:04d}",
        "status": status,
        "claim": claim.strip(),
        "evidence": evidence,
        "verified_at": verification_date,
        "supersedes": [],
        "superseded_by": [],
    }
    with settings.claims_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return row
