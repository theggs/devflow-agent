"""Snapshot and relationship tests for Iteration 3."""

from __future__ import annotations

from pathlib import Path

from app.repo.ingestion_service import build_code_intelligence_preview


def test_code_intelligence_preview_tracks_explicit_and_inferred_relationships(tmp_path: Path) -> None:
    """Python relationships should be explicit and heuristic language relationships inferred."""

    (tmp_path / "explicit.py").write_text(
        "class Explicit:\n    def call(self) -> None:\n        pass\n",
        encoding="utf-8",
    )
    (tmp_path / "inferred.js").write_text(
        "\n".join(
            [
                "class Widget {",
                "  run() {",
                "    function helper() {",
                "    }",
                "  }",
                "}",
            ]
        ),
        encoding="utf-8",
    )

    preview = build_code_intelligence_preview(tmp_path)

    explicit = [relation for relation in preview.relationships if relation.source_reference.startswith("explicit.py")]
    inferred = [relation for relation in preview.relationships if relation.source_reference.startswith("inferred.js")]

    assert preview.snapshot is not None
    assert preview.snapshot.file_count == len(preview.file_structures)
    assert preview.snapshot.relationship_count == len(preview.relationships)
    assert explicit
    assert inferred
    assert all(relation.confidence_level.value == "explicit" for relation in explicit)
    assert all(relation.confidence_level.value == "inferred" for relation in inferred)
