"""Relevance ranking logic for retrieval results."""

from __future__ import annotations

from app.schemas.retrieval import SearchResult


def apply_ranking(results: list[SearchResult]) -> list[SearchResult]:
    """Sort results by relevance_score descending.

    Serves as the baseline ranking pass; metadata boost signals are applied
    in the enhanced version used by User Story 3 (apply_ranking_with_boost).
    """

    return sorted(results, key=lambda r: r.relevance_score, reverse=True)


def apply_ranking_with_boost(
    results: list[SearchResult],
    symbol_kind_filter: str | None = None,
    path_pattern: str | None = None,
) -> list[SearchResult]:
    """Combine Qdrant similarity score with lightweight metadata boost signals.

    Boost rules (additive):
    - +0.05 when result symbol_kind matches symbol_kind_filter
    - +0.03 when source_path starts with path_pattern (path proximity)
    """

    def boosted_score(result: SearchResult) -> float:
        score = result.relevance_score
        if symbol_kind_filter and result.symbol_kind == symbol_kind_filter:
            score += 0.05
        if path_pattern:
            pattern = path_pattern.rstrip("*")
            if result.source_path.startswith(pattern):
                score += 0.03
        return score

    return sorted(results, key=boosted_score, reverse=True)
