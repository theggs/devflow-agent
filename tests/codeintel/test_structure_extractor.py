"""Structure extraction tests for Iteration 3."""

from __future__ import annotations

from pathlib import Path

from app.repo.ingestion_service import build_code_intelligence_preview


def test_code_intelligence_preview_handles_empty_and_partial_files(tmp_path: Path) -> None:
    """The preview should preserve reviewable notes for empty-symbol and heuristic files."""

    (tmp_path / "sample.py").write_text(
        "class Example:\n    def run(self) -> None:\n        pass\n",
        encoding="utf-8",
    )
    (tmp_path / "partial.js").write_text(
        "const value = 42;\nconsole.log(value);\n",
        encoding="utf-8",
    )

    preview = build_code_intelligence_preview(tmp_path)
    structures = {structure.source_path: structure for structure in preview.file_structures}

    assert "sample.py" in structures
    assert "partial.js" in structures
    assert structures["sample.py"].top_level_symbol_count == 1
    assert any("No recognizable symbols" in note for note in structures["partial.js"].structure_notes)
    assert any("heuristic parsing" in note.lower() for note in structures["partial.js"].structure_notes)
