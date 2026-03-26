"""Document and code search services for DevFlow Agent."""

from __future__ import annotations

import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

from app.config import settings
from app.rag.embedding import embed_texts
from app.rag.ranking import apply_ranking_with_boost
from app.schemas.retrieval import MetadataFilter, SearchQuery, SearchResponse, SearchResult


class ServiceUnavailableError(Exception):
    """Raised when the Qdrant vector database cannot be reached."""


class ValidationError(Exception):
    """Raised when a query or filter value fails validation."""


class NotIndexedError(Exception):
    """Raised when the requested collection is empty or does not exist."""


def _make_client() -> QdrantClient:
    return QdrantClient(host=settings.qdrant.host, port=settings.qdrant.port)


def build_qdrant_filter(metadata_filter: MetadataFilter) -> models.Filter | None:
    """Translate a MetadataFilter into a Qdrant filter.

    file_path_pattern is treated as a prefix match on source_path.
    Other fields use exact match.
    Returns None when the filter imposes no constraints.
    Raises ValidationError for unsupported content_type values.
    """

    conditions: list[models.Condition] = []

    if metadata_filter.content_type is not None:
        if metadata_filter.content_type not in ("document", "code"):
            raise ValidationError(
                f"Invalid content_type '{metadata_filter.content_type}'. Must be 'document' or 'code'."
            )
        conditions.append(
            models.FieldCondition(
                key="content_type",
                match=models.MatchValue(value=metadata_filter.content_type),
            )
        )

    if metadata_filter.symbol_kind is not None:
        conditions.append(
            models.FieldCondition(
                key="symbol_kind",
                match=models.MatchValue(value=metadata_filter.symbol_kind),
            )
        )

    if metadata_filter.repository_context is not None:
        conditions.append(
            models.FieldCondition(
                key="repository_context",
                match=models.MatchValue(value=metadata_filter.repository_context),
            )
        )

    if metadata_filter.file_path_pattern is not None:
        prefix = metadata_filter.file_path_pattern.rstrip("*")
        conditions.append(
            models.FieldCondition(
                key="source_path",
                match=models.MatchText(text=prefix),
            )
        )

    if not conditions:
        return None

    return models.Filter(must=conditions)


def _check_collection_not_empty(client: QdrantClient, collection_name: str) -> None:
    """Raise NotIndexedError if the collection is empty or does not exist."""

    try:
        info = client.get_collection(collection_name)
    except (UnexpectedResponse, Exception) as exc:
        raise NotIndexedError(
            f"Collection '{collection_name}' does not exist. Run --index first."
        ) from exc

    count = info.points_count or 0
    if count == 0:
        raise NotIndexedError(
            f"Collection '{collection_name}' is empty. Run --index first."
        )


def _validate_query(query: SearchQuery) -> None:
    if not query.query_text or not query.query_text.strip():
        raise ValidationError("query_text must not be empty.")


def _payload_to_result(payload: dict, score: float, content_type: str) -> SearchResult:
    return SearchResult(
        result_id=str(uuid.uuid4()),
        chunk_text=payload.get("chunk_text", ""),
        relevance_score=score,
        source_path=payload.get("source_path", ""),
        content_type=content_type,
        position_start=payload.get("line_start", 0),
        position_end=payload.get("line_end", 0),
        repository_context=payload.get("repository_context", ""),
        symbol_name=payload.get("symbol_name"),
        symbol_kind=payload.get("symbol_kind"),
        structural_role=payload.get("structural_role"),
    )


def search_documents(query: SearchQuery, client: QdrantClient | None = None) -> SearchResponse:
    """Search the documents Qdrant collection using semantic similarity.

    Raises ValidationError for empty query text.
    Raises ServiceUnavailableError when Qdrant is unreachable.
    Raises NotIndexedError when the collection is empty or missing.
    Returns SearchResponse with has_more=True when more results exist.
    """

    _validate_query(query)

    c = client or _make_client()

    try:
        _check_collection_not_empty(c, settings.qdrant.documents_collection)
        query_vector = embed_texts([query.query_text])[0]

        qdrant_filter = None
        if query.filters:
            qdrant_filter = build_qdrant_filter(query.filters)

        # Request one extra to detect has_more.
        fetch_limit = query.max_results + 1
        hits = c.search(
            collection_name=settings.qdrant.documents_collection,
            query_vector=query_vector,
            query_filter=qdrant_filter,
            limit=fetch_limit,
        )
    except (ServiceUnavailableError, ValidationError, NotIndexedError):
        raise
    except Exception as exc:
        raise ServiceUnavailableError(
            f"Qdrant is unavailable: {exc}"
        ) from exc

    has_more = len(hits) > query.max_results
    hits = hits[: query.max_results]

    results = [
        _payload_to_result(hit.payload or {}, hit.score, "document") for hit in hits
    ]

    path_pattern = query.filters.file_path_pattern if query.filters else None
    symbol_kind = query.filters.symbol_kind if query.filters else None
    ranked = apply_ranking_with_boost(results, symbol_kind_filter=symbol_kind, path_pattern=path_pattern)

    return SearchResponse(results=ranked, has_more=has_more)


def search_code(query: SearchQuery, client: QdrantClient | None = None) -> SearchResponse:
    """Search the code Qdrant collection using semantic similarity.

    Enriches results with symbol metadata from Qdrant payloads.
    Raises ValidationError for empty query text.
    Raises ServiceUnavailableError when Qdrant is unreachable.
    Raises NotIndexedError when the collection is empty or missing.
    Returns SearchResponse with has_more=True when more results exist.
    """

    _validate_query(query)

    c = client or _make_client()

    try:
        _check_collection_not_empty(c, settings.qdrant.code_collection)
        query_vector = embed_texts([query.query_text])[0]

        qdrant_filter = None
        if query.filters:
            qdrant_filter = build_qdrant_filter(query.filters)

        fetch_limit = query.max_results + 1
        hits = c.search(
            collection_name=settings.qdrant.code_collection,
            query_vector=query_vector,
            query_filter=qdrant_filter,
            limit=fetch_limit,
        )
    except (ServiceUnavailableError, ValidationError, NotIndexedError):
        raise
    except Exception as exc:
        raise ServiceUnavailableError(
            f"Qdrant is unavailable: {exc}"
        ) from exc

    has_more = len(hits) > query.max_results
    hits = hits[: query.max_results]

    results = [
        _payload_to_result(hit.payload or {}, hit.score, "code") for hit in hits
    ]

    path_pattern = query.filters.file_path_pattern if query.filters else None
    symbol_kind = query.filters.symbol_kind if query.filters else None
    ranked = apply_ranking_with_boost(results, symbol_kind_filter=symbol_kind, path_pattern=path_pattern)

    return SearchResponse(results=ranked, has_more=has_more)
