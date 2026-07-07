"""
Embedding Integration Package.

This package provides a provider-agnostic abstraction for embedding generation.

Architecture:

RAG / Business Services
        ↓
EmbeddingRouter
        ↓
EmbeddingProviderFactory
        ↓
Embedding Providers

Supported providers:

- Mock
- OpenAI
- Gemini
- HuggingFace
- Voyage AI
- Ollama
"""

from integrations.embeddings.base import EmbeddingProvider
from integrations.embeddings.router import EmbeddingRouter
from integrations.embeddings.factory import EmbeddingProviderFactory

from integrations.embeddings.mock_provider import MockEmbeddingProvider
from integrations.embeddings.openai_provider import OpenAIEmbeddingProvider
from integrations.embeddings.gemini_provider import GeminiEmbeddingProvider
from integrations.embeddings.huggingface_provider import HuggingFaceEmbeddingProvider
from integrations.embeddings.voyage_provider import VoyageEmbeddingProvider
from integrations.embeddings.ollama_provider import OllamaEmbeddingProvider

__all__ = [
    "EmbeddingProvider",
    "EmbeddingRouter",
    "EmbeddingProviderFactory",
    "MockEmbeddingProvider",
    "OpenAIEmbeddingProvider",
    "GeminiEmbeddingProvider",
    "HuggingFaceEmbeddingProvider",
    "VoyageEmbeddingProvider",
    "OllamaEmbeddingProvider",
]