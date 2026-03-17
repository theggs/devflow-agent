"""Repository traversal and candidate discovery."""

from __future__ import annotations

from pathlib import Path

from app.repo.content_types import detect_content_category, is_text_file
from app.repo.path_rules import should_skip_directory, to_repo_path
from app.schemas.repository_ingestion import ContentCategory, EntryType, ScanCandidate


def discover_scan_candidates(root: Path) -> list[ScanCandidate]:
    """Traverse a repository and create scan candidates for all files."""

    candidates: list[ScanCandidate] = []
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        relative_parts = path.relative_to(root).parts
        if any(should_skip_directory(part) for part in relative_parts[:-1]):
            continue

        content_category = detect_content_category(path)
        text_eligibility = "eligible" if is_text_file(path) else "ineligible"
        if content_category in {ContentCategory.BINARY, ContentCategory.MEDIA}:
            text_eligibility = "ineligible"

        candidates.append(
            ScanCandidate(
                path=to_repo_path(path, root),
                entry_type=EntryType.FILE,
                content_hint=content_category,
                discovery_source="root traversal",
                text_eligibility=text_eligibility,
            )
        )
    return candidates
