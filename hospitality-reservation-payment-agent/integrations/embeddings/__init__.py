"""
Embedding Integration Package.

Provider-agnostic abstraction for embedding generation.

Architecture:

RAG / Business Services
        ↓
EmbeddingRouter
        ↓
EmbeddingProviderFactory
        ↓
Embedding Providers

Current state:
- Base contract
- Router
- Factory
- Providers will be added incrementally
"""

from integrations.embeddings.base import EmbeddingProvider
from integrations.embeddings.router import EmbeddingRouter
from integrations.embeddings.factory import EmbeddingProviderFactory

__all__ = [
    "EmbeddingProvider",
    "EmbeddingRouter",
    "EmbeddingProviderFactory",
]