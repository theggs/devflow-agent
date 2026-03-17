"""Path-based scope rules for repository ingestion."""

from __future__ import annotations

from pathlib import Path, PurePosixPath

from app.schemas.repository_ingestion import IngestionScopeRule

DEFAULT_EXCLUDED_DIRECTORIES = {
    ".git",
    ".idea",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "venv",
}

DEFAULT_GENERATED_FILENAMES = {".DS_Store", "Thumbs.db"}


def to_repo_path(path: Path, root: Path) -> str:
    """Convert an absolute path into a repository-relative POSIX path."""

    return PurePosixPath(path.relative_to(root).as_posix()).as_posix()


def default_scope_rules() -> list[IngestionScopeRule]:
    """Return the default scope rules for Iteration 2."""

    return [
        IngestionScopeRule(
            rule_name="exclude-version-control-and-caches",
            rule_type="exclude",
            target_kind="directory",
            target_pattern="common ignored directories",
            reason="Irrelevant operational directories are outside repository understanding scope.",
            priority=10,
        ),
        IngestionScopeRule(
            rule_name="exclude-generated-and-non-text",
            rule_type="exclude",
            target_kind="content category",
            target_pattern="generated, binary, media",
            reason="Iteration 2 only ingests meaningful text-based repository content.",
            priority=20,
        ),
        IngestionScopeRule(
            rule_name="include-text-based-content",
            rule_type="include",
            target_kind="content category",
            target_pattern="source-code, documentation, configuration, text-other",
            reason="Text-based repository content is eligible for scan records and chunking.",
            priority=30,
        ),
    ]


def classify_repository_context(repo_path: str) -> str:
    """Return the top-level repository area for a relative path."""

    if "/" not in repo_path:
        return repo_path
    return repo_path.split("/", 1)[0]


def should_skip_directory(directory_name: str) -> bool:
    """Return whether a directory should be skipped during traversal."""

    return directory_name in DEFAULT_EXCLUDED_DIRECTORIES


def is_generated_filename(filename: str) -> bool:
    """Return whether a filename is always treated as generated noise."""

    return filename in DEFAULT_GENERATED_FILENAMES
