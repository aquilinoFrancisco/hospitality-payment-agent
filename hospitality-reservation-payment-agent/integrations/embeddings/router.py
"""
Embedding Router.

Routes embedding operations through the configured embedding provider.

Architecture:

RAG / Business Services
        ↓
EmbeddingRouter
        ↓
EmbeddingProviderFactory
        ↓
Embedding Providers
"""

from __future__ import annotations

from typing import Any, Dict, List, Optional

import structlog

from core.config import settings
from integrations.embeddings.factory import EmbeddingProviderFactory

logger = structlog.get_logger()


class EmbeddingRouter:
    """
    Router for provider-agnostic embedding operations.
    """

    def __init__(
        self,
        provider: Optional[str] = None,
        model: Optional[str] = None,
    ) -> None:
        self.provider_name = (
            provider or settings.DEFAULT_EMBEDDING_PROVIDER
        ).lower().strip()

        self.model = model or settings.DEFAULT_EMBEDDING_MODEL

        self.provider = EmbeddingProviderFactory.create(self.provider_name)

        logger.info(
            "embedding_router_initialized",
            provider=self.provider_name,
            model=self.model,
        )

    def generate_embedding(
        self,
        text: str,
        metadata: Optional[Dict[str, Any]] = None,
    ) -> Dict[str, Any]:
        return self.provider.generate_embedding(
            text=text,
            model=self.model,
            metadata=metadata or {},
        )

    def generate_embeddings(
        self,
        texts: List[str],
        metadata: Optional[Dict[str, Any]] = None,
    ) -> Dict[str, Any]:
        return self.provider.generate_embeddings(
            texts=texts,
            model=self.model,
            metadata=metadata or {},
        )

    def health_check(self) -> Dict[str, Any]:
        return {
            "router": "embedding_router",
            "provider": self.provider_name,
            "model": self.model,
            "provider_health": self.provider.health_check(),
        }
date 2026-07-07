# integrations/embeddings/router.py
"""
Embedding Router.

Routes embedding operations through the configured embedding provider.

Architecture:

RAG / Business Services
        ↓
EmbeddingRouter
        ↓
EmbeddingProviderFactory
        ↓
Embedding Providers
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog

from core.config import settings
from integrations.embeddings.factory import EmbeddingProviderFactory

logger = structlog.get_logger()


class EmbeddingRouter:
    """
    Router for provider-agnostic embedding operations.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.provider_name = (
            provider or settings.DEFAULT_EMBEDDING_PROVIDER
        ).lower().strip()

        self.model = model or settings.DEFAULT_EMBEDDING_MODEL

        self.provider = EmbeddingProviderFactory.create(self.provider_name)

        logger.info(
            "embedding_router_initialized",
            provider=self.provider_name,
            model=self.model,
        )

    def generate_embedding(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.provider.generate_embedding(
            text=text,
            model=self.model,
            metadata=metadata or {},
        )

    def generate_embeddings(
        self,
        texts: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.provider.generate_embeddings(
            texts=texts,
            model=self.model,
            metadata=metadata or {},
        )

    def health_check(self) -> Dict[str, Any]:
        return {
            "router": "embedding_router",
            "provider": self.provider_name,
            "model": self.model,
            "provider_health": self.provider.health_check(),
        }