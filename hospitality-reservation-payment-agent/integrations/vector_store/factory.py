# integrations/vector_store/factory.py
"""
Vector Store Factory.

Creates vector store provider implementations without exposing provider-specific
details to RAG, LangGraph, services or business workflows.
"""

from __future__ import annotations

from integrations.vector_store.base import VectorStoreProvider

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


class VectorStoreFactory:
    """
    Factory responsible for creating vector store provider implementations.
    """

    DEFAULT_PROVIDER = "memory"

    _PROVIDERS = {
        "memory": MemoryVectorStoreProvider,
        "faiss": FAISSVectorStoreProvider,
        "pgvector": PGVectorStoreProvider,
        "opensearch": OpenSearchVectorStoreProvider,
        "pinecone": PineconeVectorStoreProvider,
    }

    @classmethod
    def create(
        cls,
        provider: str | None = None,
    ) -> VectorStoreProvider:
        """
        Return a vector store provider implementation.
        """

        selected_provider = (
            provider or cls.DEFAULT_PROVIDER
        ).lower().strip()

        provider_class = cls._PROVIDERS.get(selected_provider)

        if provider_class is None:
            supported = ", ".join(
                sorted(cls._PROVIDERS.keys())
            )

            raise ValueError(
                f"Unsupported vector store provider "
                f"'{selected_provider}'. "
                f"Supported providers: {supported}"
            )

        return provider_class()

    @classmethod
    def supported_providers(cls) -> list[str]:
        """
        Return all supported vector store providers.
        """

        return sorted(cls._PROVIDERS.keys())