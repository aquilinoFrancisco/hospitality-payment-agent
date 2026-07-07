# integrations/vector_store/faiss_provider.py
"""
FAISS Vector Store Provider.

Current MVP:
- Mock implementation
- No real FAISS dependency required
- Compatible with VectorStoreProvider contract

Future:
- Connect to FAISS for local high-performance vector search.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog

from integrations.vector_store.memory_provider import MemoryVectorStoreProvider

logger = structlog.get_logger()


class FAISSVectorStoreProvider(MemoryVectorStoreProvider):
    """
    Mock FAISS implementation.

    For the MVP, this reuses the in-memory provider behavior while exposing
    FAISS as a provider-compatible option.
    """

    provider_name = "faiss"

    def health_check(self) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "status": "available",
            "mode": "mock",
            "future_engine": "faiss",
            "total_documents": len(self._documents),
        }