"""Repository ingestion tests."""

from __future__ import annotations

from pathlib import Path

from app.repo.ingestion_service import build_chunk_preview, build_scan_preview


def test_scan_preview_accepts_text_files_and_excludes_non_text() -> None:
    """The scan preview should accept text files and exclude media or binary files."""

    preview = build_scan_preview(Path.cwd())

    accepted_paths = {record.source_path for record in preview.accepted_records}
    assert "README.md" in accepted_paths
    assert "app/main.py" in accepted_paths
    assert all(not path.endswith((".png", ".jpg", ".pyc")) for path in accepted_paths)


def test_chunk_preview_builds_document_and_code_chunks() -> None:
    """The chunk preview should generate both document and code chunks for this repository."""

    preview = build_chunk_preview(Path.cwd())

    assert preview.document_chunks
    assert preview.code_chunks
    assert any(chunk.source_path == "README.md" for chunk in preview.document_chunks)
    assert any(chunk.source_path == "app/main.py" for chunk in preview.code_chunks)
