# integrations/embeddings/ollama_provider.py
"""
Ollama Embedding Provider.

Current MVP:
- Mock implementation
- No real Ollama API call
- No local model required

Future:
- Connect to Ollama Embeddings API using OLLAMA_BASE_URL
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog

from integrations.embeddings.base import EmbeddingProvider

logger = structlog.get_logger()


class OllamaEmbeddingProvider(EmbeddingProvider):
    """
    Ollama implementation of the EmbeddingProvider contract.
    """

    provider_name = "ollama"
    default_model = "nomic-embed-text"
    dimensions = 768

    def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a deterministic mock embedding.
        """

        selected_model = model or self.default_model

        logger.info(
            "ollama_embedding_generate_called",
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
        """
        Generate deterministic mock embeddings for multiple texts.
        """

        selected_model = model or self.default_model

        logger.info(
            "ollama_embeddings_generate_called",
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
        """
        Return provider health information.
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
        Generate a deterministic pseudo-embedding.

        This implementation is only intended for local development.
        """

        seed = sum(ord(char) for char in text)

        return [
            ((seed + index * 13) % 100) / 100.0
            for index in range(self.dimensions)
        ]