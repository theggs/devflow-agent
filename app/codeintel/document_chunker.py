"""Document chunk builder."""

from __future__ import annotations

from pathlib import Path

from app.codeintel.chunk_metadata import build_chunk_metadata
from app.schemas.repository_ingestion import DocumentChunk, ScanRecord


def build_document_chunks(root: Path, record: ScanRecord) -> list[DocumentChunk]:
    """Build document chunks from an accepted scan record."""

    content = (root / record.source_path).read_text(encoding="utf-8").strip()
    if not content:
        return []

    chunks: list[DocumentChunk] = []
    segments = [segment.strip() for segment in content.split("\n\n") if segment.strip()]
    if not segments:
        segments = [content]

    metadata = build_chunk_metadata(record)
    for index, segment in enumerate(segments, start=1):
        chunks.append(
            DocumentChunk(
                chunk_id=f"{record.source_path}:document:{index}",
                source_path=record.source_path,
                chunk_type=record.chunk_strategy,
                content_excerpt=segment,
                sequence_index=index,
                context_metadata=metadata,
            )
        )
    return chunks
