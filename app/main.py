"""Application entrypoint for DevFlow Agent."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.repo.ingestion_service import (
    build_and_index_repository,
    build_chunk_preview,
    build_code_intelligence_preview,
    build_scan_preview,
)


def create_app() -> dict[str, object]:
    """Return minimal application metadata for the current repository stage."""

    preview = build_code_intelligence_preview(Path.cwd())
    return {
        "name": "devflow-agent",
        "stage": "iteration-4-retrieval-experience",
        "structured_files": len(preview.file_structures),
        "symbol_inventory": len(preview.symbol_inventory),
        "relationships": len(preview.relationships),
    }


def preview_current_repository() -> dict[str, object]:
    """Return a compact preview of current repository ingestion outputs."""

    chunk_preview = build_chunk_preview(Path.cwd())
    code_preview = build_code_intelligence_preview(Path.cwd())
    return {
        "accepted_scan_records": len(chunk_preview.accepted_records),
        "excluded_paths": len(chunk_preview.excluded_paths),
        "document_chunks": len(chunk_preview.document_chunks),
        "code_chunks": len(chunk_preview.code_chunks),
        "structured_files": len(code_preview.file_structures),
        "symbol_inventory": len(code_preview.symbol_inventory),
        "relationships": len(code_preview.relationships),
        "sample_paths": [record.source_path for record in chunk_preview.accepted_records[:5]],
        "sample_symbols": [symbol.symbol_name for symbol in code_preview.symbol_inventory[:5]],
    }


def _run_index(root: Path) -> None:
    from app.rag.indexing import IndexingSummary

    summary: IndexingSummary = build_and_index_repository(root)
    print(f"Indexed {summary.document_count} document chunks, {summary.code_count} code chunks.")
    print(f"Total vectors written: {summary.total_vectors}")


def _run_search_docs(
    query_text: str,
    max_results: int,
    filter_path: str | None,
    filter_symbol_kind: str | None,
) -> None:
    from app.rag.search_service import search_documents
    from app.schemas.retrieval import MetadataFilter, SearchQuery

    filters = MetadataFilter(
        file_path_pattern=filter_path,
        symbol_kind=filter_symbol_kind,
    ) if (filter_path or filter_symbol_kind) else None

    query = SearchQuery(
        query_text=query_text,
        search_mode="document",
        filters=filters,
        max_results=max_results,
    )
    response = search_documents(query)

    if not response.results:
        print("No results found.")
        return

    for i, result in enumerate(response.results, start=1):
        print(f"\n[{i}] score={result.relevance_score:.4f}  {result.source_path}")
        print(f"    lines {result.position_start}-{result.position_end}  context={result.repository_context}")
        excerpt = result.chunk_text[:200].replace("\n", " ")
        print(f"    {excerpt}")

    if response.has_more:
        print(f"\n  ... more results available (showing top {max_results})")


def _run_search_code(
    query_text: str,
    max_results: int,
    filter_path: str | None,
    filter_symbol_kind: str | None,
) -> None:
    from app.rag.search_service import search_code
    from app.schemas.retrieval import MetadataFilter, SearchQuery

    filters = MetadataFilter(
        file_path_pattern=filter_path,
        symbol_kind=filter_symbol_kind,
    ) if (filter_path or filter_symbol_kind) else None

    query = SearchQuery(
        query_text=query_text,
        search_mode="code",
        filters=filters,
        max_results=max_results,
    )
    response = search_code(query)

    if not response.results:
        print("No results found.")
        return

    for i, result in enumerate(response.results, start=1):
        symbol_info = ""
        if result.symbol_name:
            symbol_info = f"  symbol={result.symbol_name} ({result.symbol_kind})"
        print(f"\n[{i}] score={result.relevance_score:.4f}  {result.source_path}{symbol_info}")
        print(f"    lines {result.position_start}-{result.position_end}  context={result.repository_context}")
        excerpt = result.chunk_text[:200].replace("\n", " ")
        print(f"    {excerpt}")

    if response.has_more:
        print(f"\n  ... more results available (showing top {max_results})")


def _run_lookup_symbol(
    query_name: str,
    max_results: int,
    filter_symbol_kind: str | None,
) -> None:
    from app.rag.symbol_search import lookup_symbols

    results = lookup_symbols(
        query_name=query_name,
        max_results=max_results,
        symbol_kind_filter=filter_symbol_kind,
    )

    if not results:
        print("No symbols found.")
        return

    for i, result in enumerate(results, start=1):
        parent = f"  parent={result.parent_symbol_name}" if result.parent_symbol_name else ""
        print(
            f"\n[{i}] [{result.match_quality}] {result.symbol_name} ({result.symbol_kind}){parent}"
        )
        print(f"    {result.source_path}  lines {result.line_start}-{result.line_end}")
        print(f"    role={result.structural_role}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DevFlow Agent CLI")
    group = parser.add_mutually_exclusive_group()

    group.add_argument("--index", metavar="ROOT", help="Index repository into Qdrant")
    group.add_argument("--search-docs", metavar="QUERY", help="Search document chunks by meaning")
    group.add_argument("--search-code", metavar="QUERY", help="Search code chunks by intent")
    group.add_argument("--lookup-symbol", metavar="NAME", help="Look up symbol by name")

    parser.add_argument("--max-results", type=int, default=10, help="Maximum results to return")
    parser.add_argument("--filter-path", metavar="PATTERN", help="Filter results by file path prefix")
    parser.add_argument("--filter-symbol-kind", metavar="KIND", help="Filter results by symbol kind")

    return parser


if __name__ == "__main__":
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.index is not None:
            _run_index(Path(args.index))
        elif args.search_docs is not None:
            _run_search_docs(
                args.search_docs,
                args.max_results,
                args.filter_path,
                args.filter_symbol_kind,
            )
        elif args.search_code is not None:
            _run_search_code(
                args.search_code,
                args.max_results,
                args.filter_path,
                args.filter_symbol_kind,
            )
        elif args.lookup_symbol is not None:
            _run_lookup_symbol(
                args.lookup_symbol,
                args.max_results,
                args.filter_symbol_kind,
            )
        else:
            print(preview_current_repository())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
