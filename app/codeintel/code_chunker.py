"""Code chunk builder."""

from __future__ import annotations

from pathlib import Path

from app.codeintel.chunk_metadata import build_chunk_metadata
from app.schemas.repository_ingestion import CodeChunk, ScanRecord


def build_code_chunks(root: Path, record: ScanRecord, chunk_size: int = 20) -> list[CodeChunk]:
    """Build code chunks from an accepted scan record."""

    lines = (root / record.source_path).read_text(encoding="utf-8").splitlines()
    if not lines:
        return []

    chunks: list[CodeChunk] = []
    metadata = build_chunk_metadata(record)
    for index in range(0, len(lines), chunk_size):
        excerpt = "\n".join(lines[index : index + chunk_size]).strip()
        if not excerpt:
            continue
        sequence = (index // chunk_size) + 1
        chunks.append(
            CodeChunk(
                chunk_id=f"{record.source_path}:code:{sequence}",
                source_path=record.source_path,
                chunk_type=record.chunk_strategy,
                code_excerpt=excerpt,
                sequence_index=sequence,
                context_metadata=metadata,
            )
        )
    return chunks
