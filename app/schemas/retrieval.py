"""Retrieval schemas for DevFlow Agent."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MetadataFilter:
    """Optional constraints to narrow search results by metadata attributes."""

    file_path_pattern: str | None = None
    content_type: str | None = None
    symbol_kind: str | None = None
    repository_context: str | None = None


@dataclass(frozen=True)
class SearchQuery:
    """Represents a user retrieval request."""

    query_text: str
    search_mode: str
    filters: MetadataFilter | None = None
    max_results: int = 10


@dataclass(frozen=True)
class SearchResult:
    """A single ranked entry returned by the retrieval system."""

    result_id: str
    chunk_text: str
    relevance_score: float
    source_path: str
    content_type: str
    position_start: int
    position_end: int
    repository_context: str
    symbol_name: str | None = None
    symbol_kind: str | None = None
    structural_role: str | None = None


@dataclass
class SearchResponse:
    """Wrapper for search results with pagination indicator."""

    results: list[SearchResult] = field(default_factory=list)
    has_more: bool = False


@dataclass(frozen=True)
class SymbolLookupResult:
    """A matched symbol entry returned by name lookup."""

    symbol_id: str
    symbol_name: str
    symbol_kind: str
    source_path: str
    line_start: int
    line_end: int
    structural_role: str
    match_quality: str
    parent_symbol_name: str | None = None
