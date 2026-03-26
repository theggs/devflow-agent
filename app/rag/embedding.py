"""Pluggable embedding interface for DevFlow Agent."""

from __future__ import annotations

from openai import OpenAI

from app.config import settings


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Return embedding vectors for a list of input texts.

    Uses the configured OpenAI-compatible provider and model.
    Raises ValueError for empty input lists.
    """

    if not texts:
        raise ValueError("texts must not be empty")

    client_kwargs: dict[str, object] = {"api_key": settings.embedding.api_key}
    if settings.embedding.base_url:
        client_kwargs["base_url"] = settings.embedding.base_url

    client = OpenAI(**client_kwargs)
    response = client.embeddings.create(model=settings.embedding.model, input=texts)
    return [item.embedding for item in response.data]
