# integrations/embeddings/mock_provider.py
"""
Mock Embedding Provider.

Current MVP:
- Deterministic mock embeddings
- No external API calls
- No credentials required

Purpose:
This provider allows the EmbeddingRouter and EmbeddingProviderFactory to work
without requiring OpenAI, Gemini, HuggingFace, Voyage or Ollama credentials.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog

from integrations.embeddings.base import EmbeddingProvider

logger = structlog.get_logger()


class MockEmbeddingProvider(EmbeddingProvider):
    """
    Mock implementation of the EmbeddingProvider contract.
    """

    provider_name = "mock"
    default_model = "mock-384"
    dimensions = 384

    def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a deterministic mock embedding for a single text.
        """

        selected_model = model or self.default_model

        logger.info(
            "mock_embedding_generate_called",
            model=selected_model,
            text_length=len(text),
        )

        embedding = self._mock_vector(text)

        return {
            "provider": self.provider_name,
            "model": selected_model,
            "mode": "mock",
            "embedding": embedding,
            "dimensions": len(embedding),
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
        """
        Generate deterministic mock embeddings for multiple texts.
        """

        selected_model = model or self.default_model

        logger.info(
            "mock_embeddings_generate_called",
            model=selected_model,
            input_count=len(texts),
        )

        embeddings = [
            self._mock_vector(text)
            for text in texts
        ]

        return {
            "provider": self.provider_name,
            "model": selected_model,
            "mode": "mock",
            "embeddings": embeddings,
            "dimensions": self.dimensions,
            "usage": {
                "input_count": len(texts),
                "total_characters": sum(len(text) for text in texts),
            },
            "metadata": metadata or {},
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Return mock provider health status.
        """

        return {
            "provider": self.provider_name,
            "status": "available",
            "mode": "mock",
            "default_model": self.default_model,
            "dimensions": self.dimensions,
        }

    def _mock_vector(self, text: str) -> List[float]:
        """
        Create a deterministic pseudo-embedding.

        This is not semantically meaningful.
        It is only useful for local development and architecture validation.
        """

        seed = sum(ord(char) for char in text)

        return [
            ((seed + index) % 100) / 100.0
            for index in range(self.dimensions)
        ]