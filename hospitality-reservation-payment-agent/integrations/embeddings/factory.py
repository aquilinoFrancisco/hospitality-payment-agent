# integrations/embeddings/factory.py
"""
Embedding Provider Factory.

Creates embedding provider implementations without exposing provider-specific
details to RAG, LangGraph, services or business workflows.
"""

from __future__ import annotations

from integrations.embeddings.base import EmbeddingProvider

from integrations.embeddings.mock_provider import MockEmbeddingProvider
from integrations.embeddings.openai_provider import OpenAIEmbeddingProvider
from integrations.embeddings.gemini_provider import GeminiEmbeddingProvider
from integrations.embeddings.huggingface_provider import (
    HuggingFaceEmbeddingProvider,
)
from integrations.embeddings.voyage_provider import VoyageEmbeddingProvider
from integrations.embeddings.ollama_provider import OllamaEmbeddingProvider


class EmbeddingProviderFactory:
    """
    Factory responsible for creating embedding provider implementations.
    """

    DEFAULT_PROVIDER = "mock"

    _PROVIDERS = {
        "mock": MockEmbeddingProvider,
        "openai": OpenAIEmbeddingProvider,
        "gemini": GeminiEmbeddingProvider,
        "huggingface": HuggingFaceEmbeddingProvider,
        "voyage": VoyageEmbeddingProvider,
        "ollama": OllamaEmbeddingProvider,
    }

    @classmethod
    def create(cls, provider: str | None = None) -> EmbeddingProvider:
        """
        Return an embedding provider implementation.
        """

        selected_provider = (
            provider or cls.DEFAULT_PROVIDER
        ).lower().strip()

        provider_class = cls._PROVIDERS.get(selected_provider)

        if provider_class is None:
            supported = ", ".join(sorted(cls._PROVIDERS.keys()))

            raise ValueError(
                f"Unsupported embedding provider '{selected_provider}'. "
                f"Supported providers: {supported}"
            )

        return provider_class()

    @classmethod
    def supported_providers(cls) -> list[str]:
        """
        Return all supported embedding providers.
        """

        return sorted(cls._PROVIDERS.keys())