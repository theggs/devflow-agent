"""Qdrant collection management and chunk indexing pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.config import settings
from app.rag.embedding import embed_texts
from app.schemas.code_intelligence import SymbolInventoryEntry
from app.schemas.repository_ingestion import CodeChunk, DocumentChunk

_CODE_CHUNK_SIZE = 20


@dataclass
class IndexingSummary:
    """Summary of an indexing run."""

    document_count: int
    code_count: int
    total_vectors: int


def _make_client() -> QdrantClient:
    return QdrantClient(host=settings.qdrant.host, port=settings.qdrant.port)


def ensure_collections(client: QdrantClient | None = None) -> None:
    """Create (or recreate) the documents and code Qdrant collections."""

    c = client or _make_client()
    dim = settings.embedding.dimension

    for name in (settings.qdrant.documents_collection, settings.qdrant.code_collection):
        c.recreate_collection(
            collection_name=name,
            vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
        )


def _find_best_symbol(
    source_path: str,
    line_start: int,
    line_end: int,
    symbols_by_path: dict[str, list[SymbolInventoryEntry]],
) -> SymbolInventoryEntry | None:
    """Return the best-matching symbol for a code chunk line range."""

    candidates = symbols_by_path.get(source_path, [])
    best: SymbolInventoryEntry | None = None
    best_overlap = 0

    for sym in candidates:
        overlap = min(line_end, sym.line_end) - max(line_start, sym.line_start)
        if overlap > best_overlap:
            best_overlap = overlap
            best = sym

    return best


def _build_symbols_by_path(
    symbol_inventory: list[SymbolInventoryEntry],
) -> dict[str, list[SymbolInventoryEntry]]:
    index: dict[str, list[SymbolInventoryEntry]] = {}
    for sym in symbol_inventory:
        index.setdefault(sym.source_path, []).append(sym)
    return index


def index_repository(
    root: Path,
    client: QdrantClient | None = None,
) -> IndexingSummary:
    """Index all repository chunks into Qdrant.

    Runs Iteration 2 scan+chunk pipeline, Iteration 3 code intelligence pipeline,
    generates embeddings, enriches code payloads with symbol metadata, and writes
    vector index entries to Qdrant. Idempotent: recreates collections on each run.
    """

    from app.codeintel.chunk_pipeline import build_chunks
    from app.codeintel.structure_pipeline import build_code_intelligence
    from app.repo.scan_records import build_scan_record, exclusion_reason
    from app.repo.scanner import discover_scan_candidates

    c = client or _make_client()

    # Recreate collections to ensure idempotency.
    ensure_collections(c)

    # Build scan records.
    accepted_records = []
    for candidate in discover_scan_candidates(root):
        record = build_scan_record(candidate)
        if record is not None:
            accepted_records.append(record)

    # Build chunks.
    document_chunks, code_chunks = build_chunks(accepted_records, root)

    # Build Iteration 3 symbol inventory for code enrichment.
    ci_preview = build_code_intelligence(accepted_records, root)
    symbols_by_path = _build_symbols_by_path(ci_preview.symbol_inventory)

    # Index document chunks.
    doc_texts = [chunk.content_excerpt for chunk in document_chunks]
    if doc_texts:
        doc_vectors = embed_texts(doc_texts)
        doc_points = []
        for i, (chunk, vector) in enumerate(zip(document_chunks, doc_vectors)):
            doc_points.append(
                models.PointStruct(
                    id=i,
                    vector=vector,
                    payload={
                        "chunk_id": chunk.chunk_id,
                        "source_path": chunk.source_path,
                        "repository_context": chunk.context_metadata.repository_context,
                        "chunk_text": chunk.content_excerpt,
                        "line_start": (chunk.sequence_index - 1),
                        "line_end": chunk.sequence_index,
                    },
                )
            )
        c.upsert(collection_name=settings.qdrant.documents_collection, points=doc_points)

    # Index code chunks with symbol enrichment.
    code_texts = [chunk.code_excerpt for chunk in code_chunks]
    if code_texts:
        code_vectors = embed_texts(code_texts)
        code_points = []
        for i, (chunk, vector) in enumerate(zip(code_chunks, code_vectors)):
            line_start = (chunk.sequence_index - 1) * _CODE_CHUNK_SIZE + 1
            line_end = chunk.sequence_index * _CODE_CHUNK_SIZE
            sym = _find_best_symbol(chunk.source_path, line_start, line_end, symbols_by_path)
            code_points.append(
                models.PointStruct(
                    id=i,
                    vector=vector,
                    payload={
                        "chunk_id": chunk.chunk_id,
                        "source_path": chunk.source_path,
                        "repository_context": chunk.context_metadata.repository_context,
                        "chunk_text": chunk.code_excerpt,
                        "symbol_name": sym.symbol_name if sym else None,
                        "symbol_kind": sym.symbol_kind if sym else None,
                        "structural_role": sym.structural_role.value if sym else None,
                        "line_start": line_start,
                        "line_end": line_end,
                    },
                )
            )
        c.upsert(collection_name=settings.qdrant.code_collection, points=code_points)

    total = len(document_chunks) + len(code_chunks)
    return IndexingSummary(
        document_count=len(document_chunks),
        code_count=len(code_chunks),
        total_vectors=total,
    )
