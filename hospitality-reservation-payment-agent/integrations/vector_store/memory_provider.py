# integrations/vector_store/memory_provider.py
"""
In-memory Vector Store Provider.

Current MVP:
- In-memory storage
- No external database required
- No credentials required
- Useful for local demos and architecture validation

Future:
- Replace with FAISS, PGVector, OpenSearch or Pinecone providers.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

import structlog

from integrations.vector_store.base import VectorStoreProvider

logger = structlog.get_logger()


class MemoryVectorStoreProvider(VectorStoreProvider):
    """
    In-memory implementation of the VectorStoreProvider contract.
    """

    provider_name = "memory"

    def __init__(self) -> None:
        self._documents: Dict[str, Dict[str, Any]] = {}

    def upsert_documents(
        self,
        documents: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Insert or update documents in memory.
        """

        metadata = metadata or {}

        for document in documents:
            document_id = document["id"]

            self._documents[document_id] = {
                **document,
                "metadata": {
                    **metadata, **document.get("metadata", {}),
                },
            }

        logger.info(
            "memory_vector_store_upserted",
            document_count=len(documents),
        )

        return {
            "provider": self.provider_name,
            "status": "success",
            "upserted": len(documents),
            "total_documents": len(self._documents),
        }

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Search similar documents using cosine similarity.
        """

        filters = filters or {}

        scored_results = []

        for document in self._documents.values():
            if not self._matches_filters(document, filters):
                continue

            score = self._cosine_similarity(
                query_embedding,
                document.get("embedding", []),
            )

            scored_results.append(
                {
                    "id": document.get("id"),
                    "text": document.get("text"),
                    "metadata": document.get("metadata", {}),
                    "score": score,
                }
            )

        scored_results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        results = scored_results[:top_k]

        logger.info(
            "memory_vector_store_search_completed",
            top_k=top_k,
            returned=len(results),
        )

        return {
            "provider": self.provider_name,
            "status": "success",
            "results": results,
            "top_k": top_k,
            "total_candidates": len(scored_results),
        }

    def delete_documents(
        self,
        document_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Delete documents from memory.
        """

        deleted = 0

        for document_id in document_ids:
            if document_id in self._documents:
                del self._documents[document_id]
                deleted += 1

        logger.info(
            "memory_vector_store_deleted",
            deleted=deleted,
        )

        return {
            "provider": self.provider_name,
            "status": "success",
            "deleted": deleted,
            "total_documents": len(self._documents),
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Return memory vector store health information.
        """

        return {
            "provider": self.provider_name,
            "status": "available",
            "mode": "memory",
            "total_documents": len(self._documents),
        }

    def _matches_filters(
        self,
        document: Dict[str, Any],
        filters: Dict[str, Any],
    ) -> bool:
        """
        Match document metadata against simple equality filters.
        """

        metadata = document.get("metadata", {})

        for key, expected_value in filters.items():
            if metadata.get(key) != expected_value:
                return False

        return True

    def _cosine_similarity(
        self,
        left: List[float],
        right: List[float],
    ) -> float:
        """
        Calculate cosine similarity between two vectors.
        """

        if not left or not right:
            return 0.0

        size = min(len(left), len(right))

        left_vector = left[:size]
        right_vector = right[:size]

        dot_product = sum(
            left_value * right_value
            for left_value, right_value in zip(left_vector, right_vector)
        )

        left_norm = math.sqrt(
            sum(value * value for value in left_vector)
        )

        right_norm = math.sqrt(
            sum(value * value for value in right_vector)
        )

        if left_norm == 0 or right_norm == 0:
            return 0.0

        return dot_product / (left_norm * right_norm)