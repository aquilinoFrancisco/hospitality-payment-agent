# rag/vector_store.py
"""
Vector Store abstraction for the Hospitality Reservation Payment Agent.

Current implementation:
    - In-memory vector store for MVP demos.

Future implementations:
    - PGVector
    - OpenSearch
    - FAISS
    - Pinecone
    - Weaviate
    - Elasticsearch

Design principle:
    The retriever and LangGraph workflow should depend only on the public
    VectorStore interface, not on a specific provider.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


Vector = List[float]
Metadata = Dict[str, Any]
SearchResult = Dict[str, Any]


class VectorStore(ABC):
    """
    Abstract vector store contract.

    Any future provider must implement this interface so the retriever and
    workflow do not need to change.
    """

    @abstractmethod
    def add_document(
        self,
        doc_id: str,
        content: str,
        embedding: Vector,
        metadata: Optional[Metadata] = None,
    ) -> None:
        """Add a document chunk to the vector store."""

    @abstractmethod
    def search(
        self,
        query_embedding: Vector,
        top_k: int = 3,
        filters: Optional[Metadata] = None,
    ) -> List[SearchResult]:
        """Search similar document chunks."""


class SimpleVectorStore(VectorStore):
    """
    Simple in-memory vector store for local MVP execution.

    This is intentionally lightweight and requires no external services.
    """

    def __init__(self) -> None:
        self.documents: List[SearchResult] = []

    def add_document(
        self,
        doc_id: str,
        content: str,
        embedding: Vector,
        metadata: Optional[Metadata] = None,
    ) -> None:
        """
        Add a document chunk to memory.
        """
        self.documents.append(
            {
                "id": doc_id,
                "content": content,
                "embedding": embedding,
                "metadata": metadata or {},
            }
        )

    def search(
        self,
        query_embedding: Vector,
        top_k: int = 3,
        filters: Optional[Metadata] = None,
    ) -> List[SearchResult]:
        """
        Search the most similar chunks using cosine similarity.
        """
        scored_documents: List[SearchResult] = []

        for document in self.documents:
            if filters and not _matches_filters(
                document.get("metadata", {}),
                filters,
            ):
                continue

            score = cosine_similarity(
                query_embedding,
                document["embedding"],
            )

            scored_documents.append(
                {
                    "id": document["id"],
                    "content": document["content"],
                    "metadata": document.get("metadata", {}),
                    "score": score,
                }
            )

        scored_documents.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return scored_documents[:top_k]


class PGVectorStore(VectorStore):
    """
    Future PGVector implementation.

    Intended production usage:
        - PostgreSQL
        - pgvector extension
        - indexed embedding column
        - metadata filtering
    """

    def add_document(
        self,
        doc_id: str,
        content: str,
        embedding: Vector,
        metadata: Optional[Metadata] = None,
    ) -> None:
        """
        Future implementation example:

            INSERT INTO documents (id, content, embedding, metadata)
            VALUES (...)
        """
        raise NotImplementedError(
            "PGVectorStore is not implemented in the MVP."
        )

    def search(
        self,
        query_embedding: Vector,
        top_k: int = 3,
        filters: Optional[Metadata] = None,
    ) -> List[SearchResult]:
        """
        Future implementation example:

            SELECT id, content, metadata,
                   embedding <=> query_embedding AS distance
            FROM documents
            ORDER BY distance
            LIMIT top_k
        """
        raise NotImplementedError(
            "PGVectorStore is not implemented in the MVP."
        )


class OpenSearchVectorStore(VectorStore):
    """
    Future OpenSearch implementation.

    Useful for:
        - hybrid search
        - keyword + vector search
        - enterprise search use cases
    """

    def add_document(
        self,
        doc_id: str,
        content: str,
        embedding: Vector,
        metadata: Optional[Metadata] = None,
    ) -> None:
        """
        Future implementation should index content, embedding, and metadata
        into an OpenSearch index.
        """
        raise NotImplementedError(
            "OpenSearchVectorStore is not implemented in the MVP."
        )

    def search(
        self,
        query_embedding: Vector,
        top_k: int = 3,
        filters: Optional[Metadata] = None,
    ) -> List[SearchResult]:
        """
        Future implementation should use kNN search and optional metadata
        filters.
        """
        raise NotImplementedError(
            "OpenSearchVectorStore is not implemented in the MVP."
        )


class FAISSVectorStore(VectorStore):
    """
    Future FAISS implementation.

    Useful for:
        - local high-speed vector search
        - offline demos
        - private deployments
    """

    def add_document(
        self,
        doc_id: str,
        content: str,
        embedding: Vector,
        metadata: Optional[Metadata] = None,
    ) -> None:
        """
        Future implementation should add the vector to a FAISS index and keep
        metadata in a sidecar mapping.
        """
        raise NotImplementedError(
            "FAISSVectorStore is not implemented in the MVP."
        )

    def search(
        self,
        query_embedding: Vector,
        top_k: int = 3,
        filters: Optional[Metadata] = None,
    ) -> List[SearchResult]:
        """
        Future implementation should perform nearest-neighbor search using
        FAISS and return normalized SearchResult dictionaries.
        """
        raise NotImplementedError(
            "FAISSVectorStore is not implemented in the MVP."
        )


class PineconeVectorStore(VectorStore):
    """
    Future Pinecone implementation.

    Useful for:
        - managed cloud vector search
        - scalable retrieval
        - production RAG APIs
    """

    def add_document(
        self,
        doc_id: str,
        content: str,
        embedding: Vector,
        metadata: Optional[Metadata] = None,
    ) -> None:
        """
        Future implementation should upsert vectors into a Pinecone index.
        """
        raise NotImplementedError(
            "PineconeVectorStore is not implemented in the MVP."
        )

    def search(
        self,
        query_embedding: Vector,
        top_k: int = 3,
        filters: Optional[Metadata] = None,
    ) -> List[SearchResult]:
        """
        Future implementation should query Pinecone and normalize results into
        the SearchResult contract.
        """
        raise NotImplementedError(
            "PineconeVectorStore is not implemented in the MVP."
        )


def get_vector_store(provider: str = "memory") -> VectorStore:
    """
    Vector store factory.

    Current:
        provider="memory"

    Future:
        provider="pgvector"
        provider="opensearch"
        provider="faiss"
        provider="pinecone"

    Returns:
        VectorStore implementation.
    """
    provider = provider.lower().strip()

    if provider == "memory":
        return SimpleVectorStore()

    if provider == "pgvector":
        return PGVectorStore()

    if provider == "opensearch":
        return OpenSearchVectorStore()

    if provider == "faiss":
        return FAISSVectorStore()

    if provider == "pinecone":
        return PineconeVectorStore()

    raise ValueError(
        f"Unsupported vector store provider: {provider}"
    )


def cosine_similarity(
    vector_a: Vector,
    vector_b: Vector,
) -> float:
    """
    Calculate cosine similarity between two vectors.
    """
    if not vector_a or not vector_b:
        return 0.0

    length = min(len(vector_a), len(vector_b))

    a = vector_a[:length]
    b = vector_b[:length]

    dot_product = sum(
        x * y
        for x, y in zip(a, b)
    )

    norm_a = math.sqrt(
        sum(x * x for x in a)
    )

    norm_b = math.sqrt(
        sum(y * y for y in b)
    )

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def _matches_filters(
    metadata: Metadata,
    filters: Metadata,
) -> bool:
    """
    Check whether document metadata matches all requested filters.
    """
    for key, expected_value in filters.items():

        if metadata.get(key) != expected_value:
            return False

    return True