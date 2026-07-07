# integrations/embeddings/huggingface_provider.py
"""
HuggingFace Embedding Provider.

Current MVP:
- Mock implementation
- No real Hugging Face Inference API call
- No credentials required

Future:
- Connect to Hugging Face Inference API using HUGGINGFACE_API_KEY
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog

from integrations.embeddings.base import EmbeddingProvider

logger = structlog.get_logger()


class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    """
    Hugging Face implementation of the EmbeddingProvider contract.
    """

    provider_name = "huggingface"
    default_model = "sentence-transformers/all-MiniLM-L6-v2"
    dimensions = 384

    def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        selected_model = model or self.default_model

        logger.info(
            "huggingface_embedding_generate_called",
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
            "huggingface_embeddings_generate_called",
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
        """
        Generate a deterministic mock embedding.
        """

        seed = sum(ord(char) for char in text)

        return [
            ((seed + index * 7) % 100) / 100.0
            for index in range(self.dimensions)
        ]