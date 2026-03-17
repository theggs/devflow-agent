"""Chunking pipeline for accepted scan records."""

from __future__ import annotations

from pathlib import Path

from app.codeintel.code_chunker import build_code_chunks
from app.codeintel.document_chunker import build_document_chunks
from app.schemas.repository_ingestion import ChunkStrategy, CodeChunk, DocumentChunk, ScanRecord


def build_chunks(records: list[ScanRecord], root: Path | None = None) -> tuple[list[DocumentChunk], list[CodeChunk]]:
    """Build document and code chunks from accepted scan records."""

    repository_root = root or Path.cwd()
    document_chunks: list[DocumentChunk] = []
    code_chunks: list[CodeChunk] = []

    for record in records:
        if record.chunk_strategy == ChunkStrategy.DOCUMENT:
            document_chunks.extend(build_document_chunks(repository_root, record))
            continue
        code_chunks.extend(build_code_chunks(repository_root, record))

    return document_chunks, code_chunks
