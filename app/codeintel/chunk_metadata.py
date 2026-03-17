"""Helpers for chunk metadata construction."""

from __future__ import annotations

from app.schemas.repository_ingestion import ChunkContextMetadata, ScanRecord


def build_chunk_metadata(record: ScanRecord) -> ChunkContextMetadata:
    """Build shared metadata for a chunk derived from a scan record."""

    return ChunkContextMetadata(
        source_path=record.source_path,
        repository_context=record.repository_context,
        content_category=record.content_category,
        chunk_type=record.chunk_strategy,
    )
