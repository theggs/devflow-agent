"""Helpers for structure-aware source file extraction."""

from __future__ import annotations

from pathlib import Path

from app.schemas.code_intelligence import SourceFileStructure, SymbolInventoryEntry
from app.schemas.repository_ingestion import ChunkStrategy, ReviewStatus, ScanRecord, ScopeDecision


def select_code_scan_records(records: list[ScanRecord]) -> list[ScanRecord]:
    """Return the accepted code-oriented scan records for Iteration 3."""

    return [
        record
        for record in records
        if record.scope_decision == ScopeDecision.ACCEPTED and record.chunk_strategy == ChunkStrategy.CODE
    ]


def load_source_text(root: Path, record: ScanRecord) -> str:
    """Load source text for a scan record."""

    return (root / record.source_path).read_text(encoding="utf-8")


def build_structure_notes(record: ScanRecord, symbols: list[SymbolInventoryEntry], parser_notes: list[str]) -> tuple[str, ...]:
    """Build reviewable notes for a source file structure output."""

    notes = list(parser_notes)
    if not symbols:
        notes.append("No recognizable symbols were found for this source file.")
    if Path(record.source_path).suffix.lower() != ".py":
        notes.append("Structure extraction used heuristic parsing for this non-Python source file.")
    return tuple(dict.fromkeys(notes))


def build_source_file_structure(
    record: ScanRecord,
    symbols: list[SymbolInventoryEntry],
    parser_notes: list[str] | None = None,
) -> SourceFileStructure:
    """Build the reviewable file-level structure output for a source file."""

    notes = build_structure_notes(record, symbols, parser_notes or [])
    top_level_symbol_count = sum(1 for symbol in symbols if symbol.parent_symbol_id is None)
    has_nested_symbols = any(symbol.parent_symbol_id is not None for symbol in symbols)
    return SourceFileStructure(
        source_path=record.source_path,
        repository_context=record.repository_context,
        content_category=record.content_category,
        structure_status=ReviewStatus.REVIEW_READY,
        top_level_symbol_count=top_level_symbol_count,
        has_nested_symbols=has_nested_symbols,
        structure_notes=notes,
    )
