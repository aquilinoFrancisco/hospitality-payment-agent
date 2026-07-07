# integrations/vector_store/opensearch_provider.py
"""
OpenSearch Vector Store Provider.

Current MVP:
- Mock implementation
- No OpenSearch dependency required
- Compatible with VectorStoreProvider contract

Future:
- Connect to OpenSearch k-NN vector search.
- Support hybrid retrieval: keyword + vector search.
"""

from __future__ import annotations

from typing import Dict

from integrations.vector_store.memory_provider import (
    MemoryVectorStoreProvider,
)


class OpenSearchVectorStoreProvider(MemoryVectorStoreProvider):
    """
    Mock OpenSearch implementation.

    During the MVP this provider reuses the in-memory implementation while
    exposing OpenSearch as a configurable vector store provider.

    Future implementation:
        OpenSearch
            +
        k-NN vector search
            +
        hybrid search
    """

    provider_name = "opensearch"

    def health_check(self) -> Dict[str, object]:
        """
        Return provider health information.
        """

        return {
            "provider": self.provider_name,
            "status": "available",
            "mode": "mock",
            "future_engine": "OpenSearch k-NN + Hybrid Search",
            "total_documents": len(self._documents),
        }