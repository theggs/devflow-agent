"""Exact and partial symbol-name lookup against the Iteration 3 symbol inventory."""

from __future__ import annotations

from pathlib import Path

from app.schemas.retrieval import SymbolLookupResult


def lookup_symbols(
    query_name: str,
    max_results: int = 10,
    symbol_kind_filter: str | None = None,
    root: Path | None = None,
) -> list[SymbolLookupResult]:
    """Look up symbols by exact or partial name match.

    Loads the symbol inventory from the Iteration 3 pipeline, matches by exact
    name first, then by substring. Exact matches rank above partial matches.
    Does not use embedding-based similarity.
    Returns an empty list when no symbols match.
    """

    from app.codeintel.structure_pipeline import build_code_intelligence
    from app.repo.scan_records import build_scan_record
    from app.repo.scanner import discover_scan_candidates

    repository_root = root or Path.cwd()

    accepted_records = []
    for candidate in discover_scan_candidates(repository_root):
        record = build_scan_record(candidate)
        if record is not None:
            accepted_records.append(record)

    ci_preview = build_code_intelligence(accepted_records, repository_root)
    inventory = ci_preview.symbol_inventory

    query_lower = query_name.lower()
    exact: list[SymbolLookupResult] = []
    partial: list[SymbolLookupResult] = []

    for sym in inventory:
        if symbol_kind_filter and sym.symbol_kind != symbol_kind_filter:
            continue

        name_lower = sym.symbol_name.lower()
        if name_lower == query_lower:
            match_quality = "exact"
        elif query_lower in name_lower:
            match_quality = "partial"
        else:
            continue

        result = SymbolLookupResult(
            symbol_id=sym.symbol_id,
            symbol_name=sym.symbol_name,
            symbol_kind=sym.symbol_kind,
            source_path=sym.source_path,
            line_start=sym.line_start,
            line_end=sym.line_end,
            structural_role=sym.structural_role.value,
            parent_symbol_name=sym.parent_symbol_name,
            match_quality=match_quality,
        )
        if match_quality == "exact":
            exact.append(result)
        else:
            partial.append(result)

    combined = exact + partial
    return combined[:max_results]
