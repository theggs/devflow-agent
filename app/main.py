"""Application entrypoint placeholder for DevFlow Agent."""

from __future__ import annotations

from pathlib import Path

from app.repo.ingestion_service import build_chunk_preview, build_scan_preview


def create_app() -> dict[str, object]:
    """Return minimal application metadata for the current repository stage."""

    preview = build_scan_preview(Path.cwd())
    return {
        "name": "devflow-agent",
        "stage": "iteration-2-repository-scanning-chunking",
        "accepted_scan_records": len(preview.accepted_records),
        "excluded_paths": len(preview.excluded_paths),
    }


def preview_current_repository() -> dict[str, object]:
    """Return a compact preview of current repository ingestion outputs."""

    preview = build_chunk_preview(Path.cwd())
    return {
        "accepted_scan_records": len(preview.accepted_records),
        "excluded_paths": len(preview.excluded_paths),
        "document_chunks": len(preview.document_chunks),
        "code_chunks": len(preview.code_chunks),
        "sample_paths": [record.source_path for record in preview.accepted_records[:5]],
    }


if __name__ == "__main__":
    print(preview_current_repository())
