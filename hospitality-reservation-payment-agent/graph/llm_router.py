# graph/llm_router.py
"""
LLM Router for LangGraph workflows.

This module connects LangGraph with the provider-agnostic LLM layer.

Purpose:
- Keep LangGraph independent from Gemini, OpenAI, Claude, Llama, Ollama
  or HuggingFace SDKs.
- Centralize LLM provider selection.
- Standardize LLM responses for workflow nodes.
- Keep the reservation workflow stable while LLM providers evolve.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog

from core.config import settings
from integrations.llm import LLMProviderFactory

logger = structlog.get_logger()


class LLMRouter:
    """
    Routes LangGraph LLM calls through the configured LLM provider.

    LangGraph should call this router instead of calling any provider directly.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.provider_name = provider or settings.get_default_llm_provider()
        self.model = model or settings.get_default_llm_model()

        if not settings.is_supported_llm_provider(self.provider_name):
            raise ValueError(
                f"Unsupported LLM provider: {self.provider_name}"
            )

        self.provider = LLMProviderFactory.create(self.provider_name)

        logger.info(
            "llm_router_initialized",
            provider=self.provider_name,
            model=self.model,
        )

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a single LLM response for a LangGraph node.
        """

        logger.info(
            "llm_router_generate_called",
            provider=self.provider_name,
            model=self.model,
        )

        return self.provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            model=self.model,
            temperature=(
                temperature
                if temperature is not None
                else settings.DEFAULT_LLM_TEMPERATURE
            ),
            max_tokens=(
                max_tokens
                if max_tokens is not None
                else settings.DEFAULT_LLM_MAX_TOKENS
            ),
            metadata=metadata or {},
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a chat response for a LangGraph node.
        """

        logger.info(
            "llm_router_chat_called",
            provider=self.provider_name,
            model=self.model,
            message_count=len(messages),
        )

        return self.provider.chat(
            messages=messages,
            model=self.model,
            temperature=(
                temperature
                if temperature is not None
                else settings.DEFAULT_LLM_TEMPERATURE
            ),
            max_tokens=(
                max_tokens
                if max_tokens is not None
                else settings.DEFAULT_LLM_MAX_TOKENS
            ),
            metadata=metadata or {},
        )

    def health_check(self) -> Dict[str, Any]:
        """
        Return health information for the selected provider.
        """

        provider_health = self.provider.health_check()

        return {
            "router": "llm_router",
            "provider": self.provider_name,
            "model": self.model,
            "provider_health": provider_health,
        }