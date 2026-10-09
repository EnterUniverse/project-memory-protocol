from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    project_root: Path
    memory_root: Path
    orient: tuple[str, ...]
    startup: tuple[str, ...]
    full_extra: tuple[str, ...]
    topics: dict[str, str]
    default_budget: int

    @property
    def archive_root(self) -> Path:
        return self.memory_root / "archive"

    @property
    def manifest_path(self) -> Path:
        return self.archive_root / "manifest.json"

    @property
    def source_registry_path(self) -> Path:
        return self.memory_root / "source_registry.json"

    @property
    def claims_path(self) -> Path:
        return self.memory_root / "claims" / "CLAIMS.jsonl"

    @property
    def index_path(self) -> Path:
        return self.memory_root / "index" / "memory.sqlite"


DEFAULT_ORIENT = ("RECOVERY.md", "WORKING_SET.md")
DEFAULT_STARTUP = (
    "START_HERE.md",
    "RECOVERY.md",
    "WORKING_SET.md",
    "CURRENT.md",
    "OPEN_LOOPS.md",
    "PROJECT_NARRATIVE.md",
)
DEFAULT_FULL_EXTRA = (
    "DECISIONS.md",
    "TIMELINE.md",
    "PATHS.md",
    "SOURCES.md",
    "ARCHIVE_INDEX.md",
    "claims/CLAIMS.jsonl",
    "modules/*.md",
    "stages/*.md",
)


def find_project_root(start: Path | None = None) -> Path:
    cursor = (start or Path.cwd()).resolve()
    for candidate in (cursor, *cursor.parents):
        if (candidate / ".project-memory.toml").is_file():
            return candidate
    raise FileNotFoundError("No .project-memory.toml found; run `pmem init` first.")


def load_settings(start: Path | None = None) -> Settings:
    root = find_project_root(start)
    raw = tomllib.loads((root / ".project-memory.toml").read_text(encoding="utf-8"))
    memory_name = raw.get("memory", {}).get("directory", ".project-memory")
    profiles = raw.get("profiles", {})
    return Settings(
        project_root=root,
        memory_root=(root / memory_name).resolve(),
        orient=tuple(profiles.get("orient", DEFAULT_ORIENT)),
        startup=tuple(profiles.get("startup", DEFAULT_STARTUP)),
        full_extra=tuple(profiles.get("full_extra", DEFAULT_FULL_EXTRA)),
        topics=dict(raw.get("topics", {})),
        default_budget=int(raw.get("retrieval", {}).get("default_token_budget", 12000)),
    )


def expand_memory_paths(settings: Settings, patterns: tuple[str, ...]) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        matches = sorted(settings.memory_root.glob(pattern))
        if matches:
            paths.extend(path for path in matches if path.is_file())
        else:
            candidate = settings.memory_root / pattern
            if candidate.is_file():
                paths.append(candidate)
    return list(dict.fromkeys(paths))

