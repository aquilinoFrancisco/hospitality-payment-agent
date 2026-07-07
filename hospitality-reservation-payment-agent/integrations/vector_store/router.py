# integrations/vector_store/router.py
"""
Vector Store Router.

This module is the single entry point for vector store operations.

Architecture:

RAG / Retriever
        ↓
VectorStoreRouter
        ↓
VectorStoreFactory
        ↓
Vector Store Providers

Responsibilities:
- Select the configured vector store provider.
- Delegate all vector operations.
- Keep business logic independent from provider implementations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog

from core.config import settings
from integrations.vector_store.factory import VectorStoreFactory

logger = structlog.get_logger()


class VectorStoreRouter:
    """
    Provider-agnostic router for vector store operations.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
    ) -> None:

        self.provider = (
            provider
            or settings.VECTOR_STORE_PROVIDER
        ).lower().strip()

        self.vector_store = VectorStoreFactory.create(
            self.provider
        )

    def upsert_documents(
        self,
        documents: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Insert or update embedded documents.
        """

        logger.info(
            "vector_store_upsert_requested",
            provider=self.provider,
            documents=len(documents),
        )

        return self.vector_store.upsert_documents(
            documents=documents,
            metadata=metadata,
        )

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute semantic similarity search.
        """

        logger.info(
            "vector_store_similarity_search_requested",
            provider=self.provider,
            top_k=top_k,
        )

        return self.vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters,
        )

    def delete_documents(
        self,
        document_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Delete documents from the vector store.
        """

        logger.info(
            "vector_store_delete_requested",
            provider=self.provider,
            documents=len(document_ids),
        )

        return self.vector_store.delete_documents(
            document_ids=document_ids,
        )

    def health_check(self) -> Dict[str, Any]:
        """
        Return router and provider health information.
        """

        return {
            "router": "vector_store_router",
            "provider": self.provider,
            "provider_health": self.vector_store.health_check(),
        }