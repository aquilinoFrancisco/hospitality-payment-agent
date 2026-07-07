# integrations/llm/factory.py
"""
LLM Provider Factory.

This factory creates LLM provider implementations without exposing provider
details to LangGraph, CrewAI, services, or business workflows.

Why this exists:
The platform should not depend directly on Gemini, OpenAI, Claude, Llama,
Ollama or any future LLM vendor.

Business workflows ask for an LLM provider.
The factory decides which implementation to return.
"""

from __future__ import annotations

from integrations.llm.base import LLMProvider
from integrations.llm.gemini_provider import GeminiProvider


class LLMProviderFactory:
    """
    Factory for LLM provider implementations.

    Current MVP:
        - Gemini mock provider

    Future:
        - OpenAI
        - Claude
        - Llama
        - Ollama
        - HuggingFace
    """

    @staticmethod
    def create(provider: str = "gemini") -> LLMProvider:
        """
        Return the configured LLM provider.

        Args:
            provider: Provider name.

        Returns:
            LLMProvider implementation.
        """

        provider = provider.lower().strip()

        if provider == "gemini":
            return GeminiProvider()

        raise ValueError(
            f"Unsupported LLM provider: {provider}"
        )