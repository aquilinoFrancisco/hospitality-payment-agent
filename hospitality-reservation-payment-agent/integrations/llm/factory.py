# integrations/llm/factory.py
"""
LLM Provider Factory.

This factory creates LLM provider implementations without exposing provider
details to LangGraph, CrewAI, services, or business workflows.

Business rule:

The application never depends directly on a specific LLM SDK.

Instead, every component asks the factory for an LLMProvider.

Current supported providers:

- Gemini
- OpenAI
- Claude
- Llama
- Ollama
- HuggingFace
"""

from __future__ import annotations

from integrations.llm.base import LLMProvider
from integrations.llm.gemini_provider import GeminiProvider
from integrations.llm.openai_provider import OpenAIProvider
from integrations.llm.claude_provider import ClaudeProvider
from integrations.llm.llama_provider import LlamaProvider
from integrations.llm.ollama_provider import OllamaProvider
from integrations.llm.huggingface_provider import HuggingFaceProvider


class LLMProviderFactory:
    """
    Factory responsible for creating LLM provider implementations.

    The business workflow remains completely independent from the
    underlying LLM vendor.

    Supported providers:

    - gemini
    - openai
    - claude
    - llama
    - ollama
    - huggingface
    """

    DEFAULT_PROVIDER = "gemini"

    _PROVIDERS = {
        "gemini": GeminiProvider,
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
        "llama": LlamaProvider,
        "ollama": OllamaProvider,
        "huggingface": HuggingFaceProvider,
    }

    @classmethod
    def create(
        cls,
        provider: str | None = None,
    ) -> LLMProvider:
        """
        Create an LLM provider implementation.

        Args:
            provider:
                Provider name.
                If omitted, the default provider is used.

        Returns:
            LLMProvider implementation.
        """

        selected_provider = (
            provider or cls.DEFAULT_PROVIDER
        ).lower().strip()

        provider_class = cls._PROVIDERS.get(selected_provider)

        if provider_class is None:
            supported = ", ".join(sorted(cls._PROVIDERS.keys()))

            raise ValueError(
                f"Unsupported LLM provider '{selected_provider}'. "
                f"Supported providers: {supported}"
            )

        return provider_class()

    @classmethod
    def supported_providers(cls) -> list[str]:
        """
        Return the list of supported providers.
        """

        return sorted(cls._PROVIDERS.keys())