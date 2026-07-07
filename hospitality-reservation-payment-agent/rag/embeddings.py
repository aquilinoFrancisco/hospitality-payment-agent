# rag/embeddings.py
"""
RAG Embedding Service.

This module keeps backward compatibility with the original RAG embedding
interface while delegating embedding generation to the new provider-agnostic
EmbeddingRouter.

Architecture:

RAG Pipeline
      ↓
rag.embeddings wrapper
      ↓
EmbeddingRouter
      ↓
EmbeddingProviderFactory
      ↓
Embedding Providers

Supported providers:
- mock
- openai
- gemini
- huggingface
- voyage
- ollama
"""

from __future__ import annotations

from typing import List, Optional

from core.config import settings
from integrations.embeddings import EmbeddingRouter


EMBEDDING_DIMENSION = settings.DEFAULT_EMBEDDING_DIMENSIONS


def get_text_embedding(
    text: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> List[float]:
    """
    Generate an embedding for a document.

    Backward-compatible public API.

    Existing code can still call:

        get_text_embedding(text)

    Internally, this now delegates to:

        EmbeddingRouter
            → EmbeddingProviderFactory
            → EmbeddingProvider
    """

    router = EmbeddingRouter(
        provider=provider or settings.DEFAULT_EMBEDDING_PROVIDER,
        model=model or settings.DEFAULT_EMBEDDING_MODEL,
    )

    result = router.generate_embedding(
        text=text,
        metadata={
            "source": "rag.embeddings",
        },
    )

    return result["embedding"]


def get_text_embeddings(
    texts: List[str],
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> List[List[float]]:
    """
    Generate embeddings for multiple documents.

    This function is the batch equivalent of get_text_embedding().
    """

    router = EmbeddingRouter(
        provider=provider or settings.DEFAULT_EMBEDDING_PROVIDER,
        model=model or settings.DEFAULT_EMBEDDING_MODEL,
    )

    result = router.generate_embeddings(
        texts=texts,
        metadata={
            "source": "rag.embeddings",
        },
    )

    return result["embeddings"]


def get_embedding_metadata() -> dict:
    """
    Return current embedding configuration metadata.
    """

    router = EmbeddingRouter(
        provider=settings.DEFAULT_EMBEDDING_PROVIDER,
        model=settings.DEFAULT_EMBEDDING_MODEL,
    )

    return router.health_check()