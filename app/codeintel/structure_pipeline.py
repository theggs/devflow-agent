"""Structure extraction pipeline for accepted code scan records."""

from __future__ import annotations

from pathlib import Path

from app.codeintel.relationship_metadata import build_structural_relationships
from app.codeintel.snapshot_builder import build_code_intelligence_preview
from app.codeintel.structure_extractor import (
    build_source_file_structure,
    load_source_text,
    select_code_scan_records,
)
from app.codeintel.symbol_inventory import extract_symbol_inventory
from app.schemas.code_intelligence import CodeIntelligencePreview
from app.schemas.repository_ingestion import ScanRecord


def build_code_intelligence(records: list[ScanRecord], root: Path | None = None) -> CodeIntelligencePreview:
    """Build Iteration 3 code intelligence outputs from accepted code scan records."""

    repository_root = root or Path.cwd()
    file_structures = []
    symbol_inventory = []

    for record in select_code_scan_records(records):
        content = load_source_text(repository_root, record)
        symbols, parser_notes = extract_symbol_inventory(record, content)
        file_structures.append(build_source_file_structure(record, symbols, parser_notes))
        symbol_inventory.extend(symbols)

    relationships = build_structural_relationships(file_structures, symbol_inventory)
    return build_code_intelligence_preview(
        file_structures=file_structures,
        symbols=symbol_inventory,
        relationships=relationships,
        snapshot_scope=repository_root.as_posix(),
    )
