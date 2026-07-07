"""
Embedding Integration Package.

This package provides a provider-agnostic abstraction for embedding generation.

Architecture:

RAG / Business Services
        ↓
EmbeddingRouter
        ↓
EmbeddingProviderFactory
        ↓
Embedding Providers

Current supported provider:

- MockEmbeddingProvider

Future providers:

- OpenAI
- Gemini
- Voyage AI
- HuggingFace
- Ollama
"""

from integrations.embeddings.base import EmbeddingProvider
from integrations.embeddings.router import EmbeddingRouter
from integrations.embeddings.factory import EmbeddingProviderFactory
from integrations.embeddings.mock_provider import MockEmbeddingProvider

__all__ = [
    "EmbeddingProvider",
    "EmbeddingRouter",
    "EmbeddingProviderFactory",
    "MockEmbeddingProvider",
]