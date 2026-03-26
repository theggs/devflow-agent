"""Structural relationship builders for code intelligence outputs."""

from __future__ import annotations

from app.codeintel.symbol_inventory import build_symbol_reference
from app.schemas.code_intelligence import (
    ConfidenceLevel,
    RelationshipType,
    SourceFileStructure,
    StructuralRelationship,
    SymbolInventoryEntry,
)


def _relationship_confidence(source_path: str) -> ConfidenceLevel:
    """Return the relationship confidence for a source path."""

    return ConfidenceLevel.EXPLICIT if source_path.endswith(".py") else ConfidenceLevel.INFERRED


def build_structural_relationships(
    file_structures: list[SourceFileStructure],
    symbols: list[SymbolInventoryEntry],
) -> list[StructuralRelationship]:
    """Build reviewable structural relationships between files and symbols."""

    relationships: list[StructuralRelationship] = []
    structure_by_path = {structure.source_path: structure for structure in file_structures}

    for symbol in symbols:
        confidence = _relationship_confidence(symbol.source_path)
        structure = structure_by_path.get(symbol.source_path)
        if structure is None:
            continue

        relationships.append(
            StructuralRelationship(
                relationship_type=RelationshipType.FILE_CONTAINS_SYMBOL,
                source_reference=structure.source_path,
                target_reference=build_symbol_reference(symbol),
                confidence_level=confidence,
                relationship_note="Preserves the navigation path from a source file to one extracted symbol.",
            )
        )
        relationships.append(
            StructuralRelationship(
                relationship_type=RelationshipType.SYMBOL_DEFINED_IN,
                source_reference=build_symbol_reference(symbol),
                target_reference=structure.source_path,
                confidence_level=confidence,
                relationship_note="Preserves the originating source file for the extracted symbol.",
            )
        )
        if symbol.parent_symbol_id is None:
            continue
        relationships.append(
            StructuralRelationship(
                relationship_type=RelationshipType.SYMBOL_CONTAINS_SYMBOL,
                source_reference=symbol.parent_symbol_id,
                target_reference=build_symbol_reference(symbol),
                confidence_level=confidence,
                relationship_note="Preserves parent-child containment for nested symbols.",
            )
        )

    return relationships
