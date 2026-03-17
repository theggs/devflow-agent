"""Schemas for repository scanning and chunk preparation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class EntryType(StrEnum):
    """Supported repository entry types."""

    FILE = "file"
    DIRECTORY = "directory"


class ContentCategory(StrEnum):
    """Supported content categories for repository ingestion."""

    SOURCE_CODE = "source-code"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"
    TEXT_OTHER = "text-other"
    BINARY = "binary"
    MEDIA = "media"
    GENERATED = "generated"
    UNKNOWN = "unknown"


class ScopeDecision(StrEnum):
    """Ingestion scope decision for a repository entry."""

    ACCEPTED = "accepted"
    EXCLUDED = "excluded"


class ChunkStrategy(StrEnum):
    """Chunking strategy for an accepted scan record."""

    DOCUMENT = "document"
    CODE = "code"


class ReviewStatus(StrEnum):
    """Review state for generated artifacts."""

    DRAFT = "draft"
    REVIEW_READY = "review-ready"
    VALIDATED = "validated"


@dataclass(frozen=True)
class IngestionScopeRule:
    """Represents a single include or exclude rule."""

    rule_name: str
    rule_type: str
    target_kind: str
    target_pattern: str
    reason: str
    priority: int = 0


@dataclass(frozen=True)
class ScanCandidate:
    """Represents a discovered repository entry before scope is finalized."""

    path: str
    entry_type: EntryType
    content_hint: ContentCategory
    discovery_source: str
    text_eligibility: str


@dataclass(frozen=True)
class ChunkContextMetadata:
    """Common metadata shared by scan records and chunks."""

    source_path: str
    repository_context: str
    content_category: ContentCategory
    chunk_type: ChunkStrategy


@dataclass(frozen=True)
class ScanRecord:
    """Represents an accepted text-based repository input."""

    source_path: str
    content_category: ContentCategory
    scope_decision: ScopeDecision
    repository_context: str
    chunk_strategy: ChunkStrategy
    review_status: ReviewStatus = ReviewStatus.REVIEW_READY
    exclusion_reason: str | None = None


@dataclass(frozen=True)
class DocumentChunk:
    """Represents a document-oriented chunk."""

    chunk_id: str
    source_path: str
    chunk_type: ChunkStrategy
    content_excerpt: str
    sequence_index: int
    context_metadata: ChunkContextMetadata


@dataclass(frozen=True)
class CodeChunk:
    """Represents a code-oriented chunk."""

    chunk_id: str
    source_path: str
    chunk_type: ChunkStrategy
    code_excerpt: str
    sequence_index: int
    context_metadata: ChunkContextMetadata


@dataclass
class ScanPreview:
    """Reviewable preview for repository scanning and chunk generation."""

    accepted_records: list[ScanRecord] = field(default_factory=list)
    excluded_paths: dict[str, str] = field(default_factory=dict)
    document_chunks: list[DocumentChunk] = field(default_factory=list)
    code_chunks: list[CodeChunk] = field(default_factory=list)
