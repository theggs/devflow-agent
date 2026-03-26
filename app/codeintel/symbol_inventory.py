"""Symbol inventory extraction helpers."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import PurePosixPath

from app.schemas.code_intelligence import StructuralRole, SymbolInventoryEntry
from app.schemas.repository_ingestion import ReviewStatus, ScanRecord

CONTROL_KEYWORDS = {"if", "for", "while", "switch", "catch", "else", "elif"}


@dataclass
class _SymbolDraft:
    symbol_id: str
    symbol_name: str
    symbol_kind: str
    source_path: str
    line_start: int
    line_end: int
    parent_symbol_name: str | None
    parent_symbol_id: str | None


def build_symbol_id(source_path: str, symbol_kind: str, symbol_name: str, line_start: int, line_end: int) -> str:
    """Build a stable symbol identifier."""

    return f"{source_path}:{symbol_kind}:{symbol_name}:{line_start}-{line_end}"


def build_symbol_reference(entry: SymbolInventoryEntry) -> str:
    """Return the reviewable symbol reference for an entry."""

    return entry.symbol_id


def _finalize_symbol_roles(drafts: list[_SymbolDraft]) -> list[SymbolInventoryEntry]:
    """Convert symbol drafts into reviewable symbol inventory entries."""

    child_counts: dict[str, int] = {}
    for draft in drafts:
        if draft.parent_symbol_id is None:
            continue
        child_counts[draft.parent_symbol_id] = child_counts.get(draft.parent_symbol_id, 0) + 1

    entries: list[SymbolInventoryEntry] = []
    for draft in drafts:
        role = StructuralRole.TOP_LEVEL
        if draft.parent_symbol_id is not None:
            role = StructuralRole.NESTED
        if child_counts.get(draft.symbol_id, 0) > 0:
            role = StructuralRole.CONTAINER
        entries.append(
            SymbolInventoryEntry(
                symbol_id=draft.symbol_id,
                symbol_name=draft.symbol_name,
                symbol_kind=draft.symbol_kind,
                source_path=draft.source_path,
                line_start=draft.line_start,
                line_end=draft.line_end,
                parent_symbol_name=draft.parent_symbol_name,
                parent_symbol_id=draft.parent_symbol_id,
                structural_role=role,
                review_status=ReviewStatus.REVIEW_READY,
            )
        )
    return entries


def _collect_python_symbols(
    node: ast.AST,
    source_path: str,
    drafts: list[_SymbolDraft],
    parent_draft: _SymbolDraft | None = None,
    parent_kind: str | None = None,
) -> None:
    """Collect Python symbols recursively from an AST node."""

    body = getattr(node, "body", None)
    if not isinstance(body, list):
        return

    for child in body:
        if isinstance(child, ast.ClassDef):
            kind = "class"
        elif isinstance(child, ast.FunctionDef):
            kind = "method" if parent_kind == "class" else "function"
        elif isinstance(child, ast.AsyncFunctionDef):
            kind = "async-method" if parent_kind == "class" else "async-function"
        else:
            _collect_python_symbols(child, source_path, drafts, parent_draft, parent_kind)
            continue

        line_start = getattr(child, "lineno", 1)
        line_end = getattr(child, "end_lineno", line_start)
        draft = _SymbolDraft(
            symbol_id=build_symbol_id(source_path, kind, child.name, line_start, line_end),
            symbol_name=child.name,
            symbol_kind=kind,
            source_path=source_path,
            line_start=line_start,
            line_end=line_end,
            parent_symbol_name=parent_draft.symbol_name if parent_draft else None,
            parent_symbol_id=parent_draft.symbol_id if parent_draft else None,
        )
        drafts.append(draft)
        _collect_python_symbols(child, source_path, drafts, draft, kind)


def _extract_python_symbols(record: ScanRecord, content: str) -> tuple[list[SymbolInventoryEntry], list[str]]:
    """Extract Python symbols with AST-backed structural accuracy."""

    notes: list[str] = []
    try:
        tree = ast.parse(content)
    except SyntaxError as exc:
        notes.append(f"Python parsing fell back to heuristic extraction because of a syntax error on line {exc.lineno}.")
        return _extract_heuristic_symbols(record, content, notes)

    drafts: list[_SymbolDraft] = []
    _collect_python_symbols(tree, record.source_path, drafts)
    return _finalize_symbol_roles(drafts), notes


def _extract_heuristic_symbols(
    record: ScanRecord,
    content: str,
    existing_notes: list[str] | None = None,
) -> tuple[list[SymbolInventoryEntry], list[str]]:
    """Extract symbols heuristically for non-Python sources."""

    notes = list(existing_notes or [])
    drafts: list[_SymbolDraft] = []
    stack: list[tuple[_SymbolDraft, int]] = []
    brace_depth = 0

    for line_number, line in enumerate(content.splitlines(), start=1):
        while stack and brace_depth < stack[-1][1]:
            draft, _ = stack.pop()
            draft.line_end = line_number - 1

        stripped = line.strip()
        if not stripped:
            brace_depth += line.count("{") - line.count("}")
            continue

        parent_draft = stack[-1][0] if stack else None
        symbol_match: tuple[str, str] | None = None

        class_match = re.match(r"^\s*class\s+([A-Za-z_]\w*)", line)
        function_match = re.match(r"^\s*(?:async\s+)?function\s+([A-Za-z_]\w*)\s*\(", line)
        method_match = re.match(r"^\s*([A-Za-z_]\w*)\s*\([^;]*\)\s*\{?\s*$", line)

        if class_match:
            symbol_match = (class_match.group(1), "class")
        elif function_match:
            symbol_match = (function_match.group(1), "function")
        elif method_match and method_match.group(1) not in CONTROL_KEYWORDS:
            kind = "method" if parent_draft and parent_draft.symbol_kind == "class" else "function"
            symbol_match = (method_match.group(1), kind)

        opens = line.count("{")
        closes = line.count("}")

        if symbol_match is not None:
            name, kind = symbol_match
            draft = _SymbolDraft(
                symbol_id=build_symbol_id(record.source_path, kind, name, line_number, line_number),
                symbol_name=name,
                symbol_kind=kind,
                source_path=record.source_path,
                line_start=line_number,
                line_end=line_number,
                parent_symbol_name=parent_draft.symbol_name if parent_draft else None,
                parent_symbol_id=parent_draft.symbol_id if parent_draft else None,
            )
            drafts.append(draft)
            if opens > closes:
                stack.append((draft, brace_depth + opens - closes))

        brace_depth += opens - closes

    final_line = len(content.splitlines()) or 1
    while stack:
        draft, _ = stack.pop()
        draft.line_end = final_line

    if notes or PurePosixPath(record.source_path).suffix.lower() != ".py":
        notes.append("Heuristic symbol extraction was used for this source file.")
    return _finalize_symbol_roles(drafts), list(dict.fromkeys(notes))


def extract_symbol_inventory(record: ScanRecord, content: str) -> tuple[list[SymbolInventoryEntry], list[str]]:
    """Extract symbol inventory entries for an accepted code scan record."""

    if record.source_path.endswith(".py"):
        return _extract_python_symbols(record, content)
    return _extract_heuristic_symbols(record, content)
