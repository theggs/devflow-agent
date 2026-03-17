"""Chunk pipeline tests."""

from __future__ import annotations

from pathlib import Path

from app.codeintel.chunk_pipeline import build_chunks
from app.schemas.repository_ingestion import ChunkStrategy, ContentCategory, ReviewStatus, ScanRecord, ScopeDecision


def test_build_chunks_respects_chunk_strategy() -> None:
    """Document and code records should be routed to their respective chunk builders."""

    records = [
        ScanRecord(
            source_path="README.md",
            content_category=ContentCategory.DOCUMENTATION,
            scope_decision=ScopeDecision.ACCEPTED,
            repository_context="README.md",
            chunk_strategy=ChunkStrategy.DOCUMENT,
            review_status=ReviewStatus.REVIEW_READY,
        ),
        ScanRecord(
            source_path="app/main.py",
            content_category=ContentCategory.SOURCE_CODE,
            scope_decision=ScopeDecision.ACCEPTED,
            repository_context="app",
            chunk_strategy=ChunkStrategy.CODE,
            review_status=ReviewStatus.REVIEW_READY,
        ),
    ]

    document_chunks, code_chunks = build_chunks(records, Path.cwd())

    assert document_chunks
    assert code_chunks
    assert all(chunk.chunk_type == ChunkStrategy.DOCUMENT for chunk in document_chunks)
    assert all(chunk.chunk_type == ChunkStrategy.CODE for chunk in code_chunks)
