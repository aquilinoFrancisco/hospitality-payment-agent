# integrations/llm/gemini_provider.py
"""
Gemini LLM Provider.

Current MVP:
- Mock implementation
- No real Gemini SDK call
- No credentials required

Future:
- Connect to Google Gemini API using GEMINI_API_KEY

Purpose:
This provider adapts Gemini to the common LLMProvider contract so LangGraph,
CrewAI and business workflows do not depend directly on Gemini-specific code.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog

from integrations.llm.base import LLMProvider

logger = structlog.get_logger()


class GeminiProvider(LLMProvider):
    """
    Gemini implementation of the LLMProvider contract.
    """

    provider_name = "gemini"
    default_model = "gemini-2.5-flash"

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a single mock completion.
        """

        selected_model = model or self.default_model

        logger.info(
            "gemini_generate_called",
            model=selected_model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return {
            "provider": self.provider_name,
            "model": selected_model,
            "mode": "mock",
            "content": (
                "Mock Gemini response. Replace this method with a real "
                "Gemini SDK call when production credentials are available."
            ),
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": 0,
                "total_tokens": len(prompt.split()),
            },
            "metadata": metadata or {},
        }

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a mock chat response.
        """

        selected_model = model or self.default_model

        logger.info(
            "gemini_chat_called",
            model=selected_model,
            temperature=temperature,
            max_tokens=max_tokens,
            message_count=len(messages),
        )

        last_user_message = next(
            (
                message.get("content", "")
                for message in reversed(messages)
                if message.get("role") == "user"
            ),
            "",
        )

        return {
            "provider": self.provider_name,
            "model": selected_model,
            "mode": "mock",
            "content": (
                "Mock Gemini chat response for: "
                f"{last_user_message[:120]}"
            ),
            "usage": {
                "messages": len(messages),
                "prompt_tokens": sum(
                    len(message.get("content", "").split())
                    for message in messages
                ),
                "completion_tokens": 0,
            },
            "metadata": metadata or {},
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Return Gemini provider health status.
        """

        return {
            "provider": self.provider_name,
            "status": "available",
            "mode": "mock",
            "default_model": self.default_model,
        }