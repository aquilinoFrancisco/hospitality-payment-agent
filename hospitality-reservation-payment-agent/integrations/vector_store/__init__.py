"""
Vector Store Integration Package.

This package provides a provider-agnostic abstraction for vector storage
and semantic retrieval.

Architecture:

RAG / Retriever
        ↓
VectorStoreRouter
        ↓
VectorStoreFactory
        ↓
Vector Store Providers

Supported providers:

- Memory
- FAISS
- PGVector
- OpenSearch
- Pinecone
"""

from integrations.vector_store.base import VectorStoreProvider
from integrations.vector_store.router import VectorStoreRouter
from integrations.vector_store.factory import VectorStoreFactory

from integrations.vector_store.memory_provider import (
    MemoryVectorStoreProvider,
)
from integrations.vector_store.faiss_provider import (
    FAISSVectorStoreProvider,
)
from integrations.vector_store.pgvector_provider import (
    PGVectorStoreProvider,
)
from integrations.vector_store.opensearch_provider import (
    OpenSearchVectorStoreProvider,
)
from integrations.vector_store.pinecone_provider import (
    PineconeVectorStoreProvider,
)

__all__ = [
    "VectorStoreProvider",
    "VectorStoreRouter",
    "VectorStoreFactory",
    "MemoryVectorStoreProvider",
    "FAISSVectorStoreProvider",
    "PGVectorStoreProvider",
    "OpenSearchVectorStoreProvider",
    "PineconeVectorStoreProvider",
]