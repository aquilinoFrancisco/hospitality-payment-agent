# integrations/vector_store/base.py
"""
Vector Store Provider Contract.

This module defines the provider-agnostic contract for all vector stores
supported by the platform.

Architecture:

RAG / Retriever
        ↓
VectorStoreRouter
        ↓
VectorStoreFactory
        ↓
VectorStoreProvider

Every vector store provider must implement this contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class VectorStoreProvider(ABC):
    """
    Abstract base class for vector store providers.
    """

    provider_name: str

    @abstractmethod
    def upsert_documents(
        self,
        documents: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Insert or update embedded documents in the vector store.

        Expected document format:
            {
                "id": "doc_001",
                "text": "document text",
                "embedding": [0.1, 0.2, ...],
                "metadata": {...}
            }
        """
        raise NotImplementedError

    @abstractmethod
    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Search for similar documents using a query embedding.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_documents(
        self,
        document_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Delete documents from the vector store.
        """
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Return vector store health information.
        """
        raise NotImplementedError