"""
RAG Embedding Service

This module centralizes embedding generation for the Hospitality
Reservation Payment Agent.

Current implementation:
    • Deterministic Mock Embeddings (offline)

Future implementations:
    • OpenAI
    • Azure OpenAI
    • Google Gemini
    • Voyage AI
    • HuggingFace SentenceTransformers
    • Ollama
    • Local embedding models

Only this file should change when migrating to a different provider.
The rest of the RAG pipeline remains untouched.
"""

from __future__ import annotations

import hashlib
from typing import List

EMBEDDING_DIMENSION = 384


# ==========================================================
# Public API
# ==========================================================

def get_text_embedding(text: str) -> List[float]:
    """
    Generate an embedding for a document.

    Current implementation:
        Deterministic mock embedding.

    Production:
        Replace the return statement with any provider.

    Args:
        text:
            Document text.

    Returns:
        List[float]
    """

    return _mock_embedding(text)

    # ----------------------------------------------------------
    # Future implementation examples
    # ----------------------------------------------------------

    # return _openai_embedding(text)

    # return _azure_openai_embedding(text)

    # return _sentence_transformer_embedding(text)

    # return _ollama_embedding(text)


# ==========================================================
# Current Mock Implementation
# ==========================================================

def _mock_embedding(text: str) -> List[float]:
    """
    Deterministic pseudo-embedding.

    Advantages

    - Offline
    - Fast
    - No API keys
    - Deterministic
    - Perfect for MVP demos

    It is NOT intended for semantic similarity.
    """

    digest = hashlib.sha256(
        text.encode("utf-8")
    ).digest()

    embedding: List[float] = []

    while len(embedding) < EMBEDDING_DIMENSION:

        for byte in digest:

            embedding.append(byte / 255.0)

            if len(embedding) >= EMBEDDING_DIMENSION:
                break

    return embedding


# ==========================================================
# Future Providers
# ==========================================================

def _openai_embedding(text: str) -> List[float]:
    """
    OpenAI Embeddings.

    Example implementation:

        from openai import OpenAI

        client = OpenAI()

        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )

        return response.data[0].embedding

    Suggested models

    - text-embedding-3-small
    - text-embedding-3-large
    """

    raise NotImplementedError(
        "OpenAI embedding provider not implemented."
    )


def _azure_openai_embedding(text: str) -> List[float]:
    """
    Azure OpenAI Embeddings.

    Example:

        AzureOpenAI(
            api_key=...,
            api_version="2024-02-01",
            azure_endpoint="..."
        )

    return response.data[0].embedding
    """

    raise NotImplementedError(
        "Azure OpenAI provider not implemented."
    )


def _sentence_transformer_embedding(text: str) -> List[float]:
    """
    Local HuggingFace embedding model.

    Example

        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

        return model.encode(text).tolist()

    Other good models

    - all-MiniLM-L6-v2
    - bge-base-en-v1.5
    - e5-base-v2
    """

    raise NotImplementedError(
        "SentenceTransformer provider not implemented."
    )


def _ollama_embedding(text: str) -> List[float]:
    """
    Ollama local embeddings.

    Example

        POST /api/embeddings

        {
            "model": "nomic-embed-text",
            "prompt": text
        }

    Models

    - nomic-embed-text
    - bge-large
    """

    raise NotImplementedError(
        "Ollama provider not implemented."
    )