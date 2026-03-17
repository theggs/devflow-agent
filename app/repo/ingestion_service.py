"""High-level repository ingestion orchestration."""

from __future__ import annotations

from pathlib import Path

from app.codeintel.chunk_pipeline import build_chunks
from app.repo.scan_records import build_scan_record, exclusion_reason
from app.repo.scanner import discover_scan_candidates
from app.schemas.repository_ingestion import ScanPreview


def build_scan_preview(root: Path) -> ScanPreview:
    """Build a reviewable preview of scan records and exclusions."""

    preview = ScanPreview()
    for candidate in discover_scan_candidates(root):
        record = build_scan_record(candidate)
        if record is None:
            preview.excluded_paths[candidate.path] = exclusion_reason(candidate) or "Excluded from scan scope."
            continue
        preview.accepted_records.append(record)
    return preview


def build_chunk_preview(root: Path) -> ScanPreview:
    """Build a reviewable preview that includes chunks for accepted scan records."""

    preview = build_scan_preview(root)
    document_chunks, code_chunks = build_chunks(preview.accepted_records)
    preview.document_chunks = document_chunks
    preview.code_chunks = code_chunks
    return preview
