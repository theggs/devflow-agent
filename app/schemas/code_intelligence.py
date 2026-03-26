"""Schemas for repository code intelligence extraction."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from app.schemas.repository_ingestion import ContentCategory, ReviewStatus


class StructuralRole(StrEnum):
    """Supported structural roles for extracted symbols."""

    TOP_LEVEL = "top-level"
    NESTED = "nested"
    CONTAINER = "container"


class RelationshipType(StrEnum):
    """Supported relationship types for code intelligence outputs."""

    FILE_CONTAINS_SYMBOL = "file-contains-symbol"
    SYMBOL_CONTAINS_SYMBOL = "symbol-contains-symbol"
    SYMBOL_DEFINED_IN = "symbol-defined-in"


class ConfidenceLevel(StrEnum):
    """Confidence level for extracted structural relationships."""

    EXPLICIT = "explicit"
    INFERRED = "inferred"


@dataclass(frozen=True)
class SourceFileStructure:
    """Reviewable structure-aware view of a source file."""

    source_path: str
    repository_context: str
    content_category: ContentCategory
    structure_status: ReviewStatus = ReviewStatus.REVIEW_READY
    top_level_symbol_count: int = 0
    has_nested_symbols: bool = False
    structure_notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class SymbolInventoryEntry:
    """Reviewable symbol inventory entry."""

    symbol_id: str
    symbol_name: str
    symbol_kind: str
    source_path: str
    line_start: int
    line_end: int
    parent_symbol_name: str | None = None
    parent_symbol_id: str | None = None
    structural_role: StructuralRole = StructuralRole.TOP_LEVEL
    review_status: ReviewStatus = ReviewStatus.REVIEW_READY


@dataclass(frozen=True)
class StructuralRelationship:
    """Reviewable relationship between files and symbols."""

    relationship_type: RelationshipType
    source_reference: str
    target_reference: str
    confidence_level: ConfidenceLevel
    relationship_note: str


@dataclass(frozen=True)
class CodeIntelligenceSnapshot:
    """Snapshot summary for one code intelligence extraction pass."""

    snapshot_scope: str
    file_count: int
    symbol_count: int
    relationship_count: int
    snapshot_status: ReviewStatus = ReviewStatus.REVIEW_READY


@dataclass
class CodeIntelligencePreview:
    """Reviewable preview for Iteration 3 structure extraction outputs."""

    file_structures: list[SourceFileStructure] = field(default_factory=list)
    symbol_inventory: list[SymbolInventoryEntry] = field(default_factory=list)
    relationships: list[StructuralRelationship] = field(default_factory=list)
    snapshot: CodeIntelligenceSnapshot | None = None
