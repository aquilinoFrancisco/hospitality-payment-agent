# integrations/vector_store/pgvector_provider.py
"""
PGVector Vector Store Provider.

Current MVP:
- Mock implementation
- No PostgreSQL dependency required
- Compatible with VectorStoreProvider contract

Future:
- Connect to PostgreSQL + PGVector extension.
"""

from __future__ import annotations

from typing import Dict

from integrations.vector_store.memory_provider import (
    MemoryVectorStoreProvider,
)


class PGVectorStoreProvider(MemoryVectorStoreProvider):
    """
    Mock PGVector implementation.

    During the MVP this provider reuses the in-memory implementation while
    exposing PGVector as a configurable provider.

    Future implementation:
        PostgreSQL
            +
        PGVector extension
    """

    provider_name = "pgvector"

    def health_check(self) -> Dict[str, object]:
        """
        Return provider health information.
        """

        return {
            "provider": self.provider_name,
            "status": "available",
            "mode": "mock",
            "future_engine": "PostgreSQL + PGVector",
            "total_documents": len(self._documents),
        }