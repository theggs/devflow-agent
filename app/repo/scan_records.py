"""Scan-record construction and exclusion reasoning."""

from __future__ import annotations

from app.repo.content_types import select_chunk_strategy
from app.repo.path_rules import classify_repository_context
from app.schemas.repository_ingestion import (
    ContentCategory,
    ScanCandidate,
    ScanRecord,
    ScopeDecision,
)


def exclusion_reason(candidate: ScanCandidate) -> str | None:
    """Return the exclusion reason for a candidate, when applicable."""

    if candidate.content_hint == ContentCategory.MEDIA:
        return "Excluded media asset outside Iteration 2 text-only scope."
    if candidate.content_hint == ContentCategory.BINARY:
        return "Excluded binary file outside Iteration 2 text-only scope."
    if candidate.text_eligibility != "eligible":
        return "Excluded non-text content that cannot produce reviewable chunks."
    return None


def build_scan_record(candidate: ScanCandidate) -> ScanRecord | None:
    """Convert an eligible candidate into a scan record."""

    reason = exclusion_reason(candidate)
    if reason is not None:
        return None

    return ScanRecord(
        source_path=candidate.path,
        content_category=candidate.content_hint,
        scope_decision=ScopeDecision.ACCEPTED,
        repository_context=classify_repository_context(candidate.path),
        chunk_strategy=select_chunk_strategy(candidate.content_hint),
    )
