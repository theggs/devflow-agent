"""Snapshot builders for code intelligence outputs."""

from __future__ import annotations

from app.schemas.code_intelligence import (
    CodeIntelligencePreview,
    CodeIntelligenceSnapshot,
    SourceFileStructure,
    StructuralRelationship,
    SymbolInventoryEntry,
)
from app.schemas.repository_ingestion import ReviewStatus


def build_code_intelligence_snapshot(
    file_structures: list[SourceFileStructure],
    symbols: list[SymbolInventoryEntry],
    relationships: list[StructuralRelationship],
    snapshot_scope: str = "repository-root",
) -> CodeIntelligenceSnapshot:
    """Build the reviewable Iteration 3 snapshot summary."""

    return CodeIntelligenceSnapshot(
        snapshot_scope=snapshot_scope,
        file_count=len(file_structures),
        symbol_count=len(symbols),
        relationship_count=len(relationships),
        snapshot_status=ReviewStatus.REVIEW_READY,
    )


def build_code_intelligence_preview(
    file_structures: list[SourceFileStructure],
    symbols: list[SymbolInventoryEntry],
    relationships: list[StructuralRelationship],
    snapshot_scope: str = "repository-root",
) -> CodeIntelligencePreview:
    """Build the reviewable Iteration 3 preview bundle."""

    return CodeIntelligencePreview(
        file_structures=file_structures,
        symbol_inventory=symbols,
        relationships=relationships,
        snapshot=build_code_intelligence_snapshot(
            file_structures=file_structures,
            symbols=symbols,
            relationships=relationships,
            snapshot_scope=snapshot_scope,
        ),
    )
