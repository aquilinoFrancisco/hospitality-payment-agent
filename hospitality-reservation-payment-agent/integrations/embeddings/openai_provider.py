# integrations/embeddings/openai_provider.py
"""
OpenAI Embedding Provider.

Current MVP:
- Mock implementation
- No real OpenAI SDK call
- No credentials required

Future:
- Connect to OpenAI Embeddings API using OPENAI_API_KEY
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog

from integrations.embeddings.base import EmbeddingProvider

logger = structlog.get_logger()


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    OpenAI implementation of the EmbeddingProvider contract.
    """

    provider_name = "openai"
    default_model = "text-embedding-3-small"
    dimensions = 1536

    def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        selected_model = model or self.default_model

        logger.info(
            "openai_embedding_generate_called",
            model=selected_model,
            text_length=len(text),
        )

        return {
            "provider": self.provider_name,
            "model": selected_model,
            "mode": "mock",
            "embedding": self._mock_vector(text),
            "dimensions": self.dimensions,
            "usage": {
                "input_count": 1,
                "total_characters": len(text),
            },
            "metadata": metadata or {},
        }

    def generate_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        selected_model = model or self.default_model

        logger.info(
            "openai_embeddings_generate_called",
            model=selected_model,
            input_count=len(texts),
        )

        return {
            "provider": self.provider_name,
            "model": selected_model,
            "mode": "mock",
            "embeddings": [
                self._mock_vector(text)
                for text in texts
            ],
            "dimensions": self.dimensions,
            "usage": {
                "input_count": len(texts),
                "total_characters": sum(len(text) for text in texts),
            },
            "metadata": metadata or {},
        }

    def health_check(self) -> Dict[str, Any]:
        return {
            "provider": self.provider_name,
            "status": "available",
            "mode": "mock",
            "default_model": self.default_model,
            "dimensions": self.dimensions,
        }

    def _mock_vector(self, text: str) -> List[float]:
        seed = sum(ord(char) for char in text)

        return [
            ((seed + index * 3) % 100) / 100.0
            for index in range(self.dimensions)
        ]