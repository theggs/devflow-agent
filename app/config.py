"""Configuration for DevFlow Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class QdrantSettings:
    """Qdrant vector database connection settings."""

    host: str = "localhost"
    port: int = 6333
    documents_collection: str = "documents"
    code_collection: str = "code"


@dataclass(frozen=True)
class EmbeddingSettings:
    """Embedding provider settings."""

    api_key: str = field(default_factory=lambda: os.environ.get("OPENAI_API_KEY", ""))
    model: str = "text-embedding-3-small"
    dimension: int = 1536
    base_url: str | None = field(default_factory=lambda: os.environ.get("OPENAI_BASE_URL") or None)


@dataclass(frozen=True)
class Settings:
    """Application settings for DevFlow Agent."""

    app_name: str = "DevFlow Agent"
    environment: str = "development"
    qdrant: QdrantSettings = field(default_factory=QdrantSettings)
    embedding: EmbeddingSettings = field(default_factory=EmbeddingSettings)


settings = Settings()
