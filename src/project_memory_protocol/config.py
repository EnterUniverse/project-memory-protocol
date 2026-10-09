from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from .util import resolve_inside


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
    "RECOVERY.md",
    "WORKING_SET.md",
    "CURRENT.md",
    "OPEN_LOOPS.md",
    "DECISIONS.md",
)
DEFAULT_FULL_EXTRA = (
    "PROJECT_NARRATIVE.md",
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
    memory = raw.get("memory", {})
    profiles = raw.get("profiles", {})
    retrieval = raw.get("retrieval", {})
    topics = raw.get("topics", {})
    if not all(isinstance(table, dict) for table in (memory, profiles, retrieval, topics)):
        raise TypeError("memory, profiles, retrieval, and topics must be TOML tables")
    memory_name = memory.get("directory", ".project-memory")
    if not isinstance(memory_name, str) or not memory_name.strip():
        raise ValueError("memory.directory must be a non-empty relative path")
    try:
        memory_root = resolve_inside(root, memory_name)
    except ValueError as error:
        raise ValueError("memory.directory must stay inside the project root") from error
    profile_values = {}
    for name, default in (
        ("orient", DEFAULT_ORIENT),
        ("startup", DEFAULT_STARTUP),
        ("full_extra", DEFAULT_FULL_EXTRA),
    ):
        value = profiles.get(name, default)
        if not isinstance(value, list | tuple) or not all(isinstance(item, str) for item in value):
            raise TypeError(f"profiles.{name} must be an array of paths")
        profile_values[name] = tuple(value)
    if not all(isinstance(key, str) and isinstance(value, str) for key, value in topics.items()):
        raise TypeError("topic names and paths must be strings")
    budget = int(retrieval.get("default_token_budget", 12000))
    if budget <= 0:
        raise ValueError("retrieval.default_token_budget must be positive")
    return Settings(
        project_root=root,
        memory_root=memory_root,
        orient=profile_values["orient"],
        startup=profile_values["startup"],
        full_extra=profile_values["full_extra"],
        topics=dict(topics),
        default_budget=budget,
    )


def expand_memory_paths(settings: Settings, patterns: tuple[str, ...]) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        pattern_path = Path(pattern)
        if pattern_path.is_absolute() or ".." in pattern_path.parts:
            raise ValueError(f"memory path must stay inside the memory directory: {pattern}")
        matches = sorted(settings.memory_root.glob(pattern))
        if matches:
            paths.extend(path for path in matches if path.is_file())
        else:
            candidate = settings.memory_root / pattern
            if candidate.is_file():
                paths.append(candidate)
    return list(dict.fromkeys(paths))
