from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    excerpt: str


BUILTIN_RULES = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "unix-home-path": re.compile(r"/(?:home|Users)/[^/\s]+/"),
    "windows-user-path": re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\"),
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github-token": re.compile(r"\bgh[opusr]_[A-Za-z0-9]{30,}\b"),
    "generic-secret": re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|secret[_-]?key)\b\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{12,}"
    ),
}

TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".toml",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".sh",
}


def load_blocklist(path: Path | None) -> list[str]:
    if path is None or not path.is_file():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def scan(root: Path, blocklist_path: Path | None = None) -> list[Finding]:
    root = root.resolve()
    if not root.exists():
        raise FileNotFoundError(root)
    blocked = load_blocklist(blocklist_path)
    findings: list[Finding] = []
    candidates = [root] if root.is_file() else sorted(root.rglob("*"))
    for path in candidates:
        if (
            path.is_symlink()
            or not path.is_file()
            or any(part in {".git", ".venv", "dist", "build"} for part in path.parts)
        ):
            continue
        if path.suffix and path.suffix.casefold() not in TEXT_SUFFIXES:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, 1):
            redacted = line
            for pattern in BUILTIN_RULES.values():
                redacted = pattern.sub("[REDACTED]", redacted)
            for private_term in blocked:
                redacted = re.sub(
                    re.escape(private_term), "[REDACTED]", redacted, flags=re.IGNORECASE
                )
            for rule, pattern in BUILTIN_RULES.items():
                if pattern.search(line):
                    findings.append(
                        Finding(
                            path.name if root.is_file() else str(path.relative_to(root)),
                            line_number,
                            rule,
                            redacted.strip()[:200],
                        )
                    )
            folded = line.casefold()
            for private_term in blocked:
                if private_term.casefold() in folded:
                    findings.append(
                        Finding(
                            path.name if root.is_file() else str(path.relative_to(root)),
                            line_number,
                            "private-blocklist",
                            redacted.strip()[:200],
                        )
                    )
    return findings
