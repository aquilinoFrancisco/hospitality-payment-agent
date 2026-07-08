# integrations/embeddings/base.py
"""
Embedding Provider Contract.

This module defines the provider-agnostic contract for all embedding
providers supported by the platform.

Architecture:

Business Services
        │
        ▼
Embedding Router
        │
        ▼
Embedding Provider Factory
        │
        ▼
Embedding Provider

Every embedding provider must implement this contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class EmbeddingProvider(ABC):
    """
    Abstract base class for embedding providers.
    """

    provider_name: str
    default_model: str

    @abstractmethod
    def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate an embedding vector from a text.

        Returns:
            Normalized embedding response.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate embedding vectors for multiple texts.

        Returns:
            Normalized embedding response.
        """
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Verify provider availability.

        Returns:
            Health information.
        """
        raise NotImplementedError