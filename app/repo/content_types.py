"""Content classification helpers for repository ingestion."""

from __future__ import annotations

from pathlib import Path

from app.schemas.repository_ingestion import ChunkStrategy, ContentCategory

SOURCE_CODE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".css",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".json",
    ".kt",
    ".m",
    ".mdx",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".sql",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".xml",
    ".yaml",
    ".yml",
}
DOCUMENTATION_EXTENSIONS = {".md", ".rst", ".txt"}
CONFIGURATION_FILENAMES = {
    "docker-compose.yml",
    "makefile",
    "pyproject.toml",
}
MEDIA_EXTENSIONS = {
    ".gif",
    ".jpeg",
    ".jpg",
    ".mp3",
    ".mp4",
    ".pdf",
    ".png",
    ".svg",
    ".wav",
}
BINARY_EXTENSIONS = {
    ".a",
    ".bin",
    ".class",
    ".dll",
    ".dylib",
    ".exe",
    ".o",
    ".obj",
    ".pyc",
    ".so",
    ".zip",
}
TEXT_READ_SIZE = 2048


def is_text_file(path: Path) -> bool:
    """Heuristically determine whether a file is text-based."""

    suffix = path.suffix.lower()
    name = path.name.lower()
    if suffix in MEDIA_EXTENSIONS or suffix in BINARY_EXTENSIONS:
        return False
    if suffix in SOURCE_CODE_EXTENSIONS or suffix in DOCUMENTATION_EXTENSIONS:
        return True
    if name in CONFIGURATION_FILENAMES or name.startswith(".env"):
        return True

    try:
        sample = path.read_bytes()[:TEXT_READ_SIZE]
    except OSError:
        return False

    if b"\x00" in sample:
        return False

    try:
        sample.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def detect_content_category(path: Path) -> ContentCategory:
    """Classify a repository file into a content category."""

    suffix = path.suffix.lower()
    name = path.name.lower()
    if suffix in MEDIA_EXTENSIONS:
        return ContentCategory.MEDIA
    if suffix in BINARY_EXTENSIONS:
        return ContentCategory.BINARY
    if suffix in DOCUMENTATION_EXTENSIONS or name == "readme.md":
        return ContentCategory.DOCUMENTATION
    if name in CONFIGURATION_FILENAMES or name.startswith(".env"):
        return ContentCategory.CONFIGURATION
    if suffix in SOURCE_CODE_EXTENSIONS:
        if suffix in {".json", ".toml", ".yaml", ".yml"}:
            return ContentCategory.CONFIGURATION
        return ContentCategory.SOURCE_CODE
    if is_text_file(path):
        return ContentCategory.TEXT_OTHER
    return ContentCategory.UNKNOWN


def select_chunk_strategy(content_category: ContentCategory) -> ChunkStrategy:
    """Choose the chunk strategy for an accepted content category."""

    if content_category == ContentCategory.SOURCE_CODE:
        return ChunkStrategy.CODE
    return ChunkStrategy.DOCUMENT
