# rag/vector_store.py
"""
RAG Vector Store Service.

This module keeps backward compatibility with the original RAG vector store
interface while delegating vector storage and semantic retrieval to the new
provider-agnostic VectorStoreRouter.

Architecture:

RAG / Retriever
      ↓
rag.vector_store wrapper
      ↓
VectorStoreRouter
      ↓
VectorStoreFactory
      ↓
Vector Store Providers

Supported providers:
- memory
- faiss
- pgvector
- opensearch
- pinecone
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.config import settings
from integrations.vector_store import VectorStoreRouter


Vector = List[float]
Metadata = Dict[str, Any]
SearchResult = Dict[str, Any]


class VectorStore:
    """
    Backward-compatible vector store wrapper.

    Existing RAG code can still call:

        add_document()
        search()

    Internally, this wrapper delegates all operations to VectorStoreRouter.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
    ) -> None:
        self.provider = provider or settings.VECTOR_STORE_PROVIDER
        self.router = VectorStoreRouter(provider=self.provider)

    def add_document(
        self,
        doc_id: str,
        content: str,
        embedding: Vector,
        metadata: Optional[Metadata] = None,
    ) -> None:
        """
        Add a document chunk to the configured vector store.
        """

        self.router.upsert_documents(
            documents=[
                {
                    "id": doc_id,
                    "text": content,
                    "embedding": embedding,
                    "metadata": metadata or {},
                }
            ],
            metadata={
                "source": "rag.vector_store",
            },
        )

    def search(
        self,
        query_embedding: Vector,
        top_k: int = 3,
        filters: Optional[Metadata] = None,
    ) -> List[SearchResult]:
        """
        Search similar document chunks.
        """

        result = self.router.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters,
        )

        return [
            {
                "id": item.get("id"),
                "content": item.get("text"),
                "metadata": item.get("metadata", {}),
                "score": item.get("score", 0.0),
            }
            for item in result.get("results", [])
        ]

    def health_check(self) -> Dict[str, Any]:
        """
        Return vector store health metadata.
        """

        return self.router.health_check()


class SimpleVectorStore(VectorStore):
    """
    Backward-compatible alias for the in-memory vector store.
    """

    def __init__(self) -> None:
        super().__init__(provider="memory")


def get_vector_store(
    provider: Optional[str] = None,
) -> VectorStore:
    """
    Return a backward-compatible vector store wrapper.

    Existing code can still call:

        get_vector_store("memory")

    Internally, this now delegates to:

        VectorStoreRouter
            → VectorStoreFactory
            → VectorStoreProvider
    """

    selected_provider = (
        provider
        or settings.VECTOR_STORE_PROVIDER
    ).lower().strip()

    return VectorStore(provider=selected_provider)


def upsert_documents(
    documents: List[Dict[str, Any]],
    provider: Optional[str] = None,
    metadata: Optional[Metadata] = None,
) -> Dict[str, Any]:
    """
    Upsert embedded documents through the provider-agnostic router.
    """

    router = VectorStoreRouter(
        provider=provider or settings.VECTOR_STORE_PROVIDER,
    )

    return router.upsert_documents(
        documents=documents,
        metadata=metadata or {
            "source": "rag.vector_store",
        },
    )


def similarity_search(
    query_embedding: Vector,
    top_k: int = 3,
    provider: Optional[str] = None,
    filters: Optional[Metadata] = None,
) -> Dict[str, Any]:
    """
    Execute semantic similarity search through the configured vector store.
    """

    router = VectorStoreRouter(
        provider=provider or settings.VECTOR_STORE_PROVIDER,
    )

    return router.similarity_search(
        query_embedding=query_embedding,
        top_k=top_k,
        filters=filters,
    )


def get_vector_store_metadata(
    provider: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Return current vector store configuration metadata.
    """

    router = VectorStoreRouter(
        provider=provider or settings.VECTOR_STORE_PROVIDER,
    )

    return router.health_check()