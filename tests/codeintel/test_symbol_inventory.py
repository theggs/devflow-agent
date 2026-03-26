"""Symbol inventory tests for Iteration 3."""

from __future__ import annotations

from pathlib import Path

from app.repo.ingestion_service import build_code_intelligence_preview


def test_symbol_inventory_distinguishes_repeated_and_nested_symbols(tmp_path: Path) -> None:
    """Repeated names and nested roles should remain distinguishable."""

    (tmp_path / "inventory.py").write_text(
        "\n".join(
            [
                "class Runner:",
                "    def run(self) -> None:",
                "        def helper() -> None:",
                "            pass",
                "",
                "def run() -> None:",
                "    pass",
            ]
        ),
        encoding="utf-8",
    )

    preview = build_code_intelligence_preview(tmp_path)
    symbols = [symbol for symbol in preview.symbol_inventory if symbol.source_path == "inventory.py"]
    run_symbols = [symbol for symbol in symbols if symbol.symbol_name == "run"]

    assert len(run_symbols) == 2
    assert len({symbol.symbol_id for symbol in run_symbols}) == 2
    assert any(symbol.parent_symbol_name == "Runner" for symbol in run_symbols)
    assert any(symbol.parent_symbol_name is None for symbol in run_symbols)
    assert any(symbol.structural_role.value == "container" for symbol in symbols if symbol.symbol_name == "run")
