# integrations/llm/huggingface_provider.py
"""
HuggingFace LLM Provider.

Current MVP:
- Mock implementation
- No real HuggingFace API call
- No credentials required

Future:
- Connect to HuggingFace Inference API
- Connect to Text Generation Inference (TGI)
- Connect to local Transformers pipelines

Purpose:
This provider adapts HuggingFace-based models to the common LLMProvider
contract so LangGraph, CrewAI and business workflows remain independent
from deployment details.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog

from integrations.llm.base import LLMProvider

logger = structlog.get_logger()


class HuggingFaceProvider(LLMProvider):
    """
    HuggingFace implementation of the LLMProvider contract.
    """

    provider_name = "huggingface"
    default_model = "mistralai/Mistral-7B-Instruct-v0.3"

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        selected_model = model or self.default_model

        logger.info(
            "huggingface_generate_called",
            model=selected_model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return {
            "provider": self.provider_name,
            "model": selected_model,
            "mode": "mock",
            "content": (
                "Mock HuggingFace response. Replace this implementation "
                "with HuggingFace Inference API, TGI, or Transformers."
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

        selected_model = model or self.default_model

        logger.info(
            "huggingface_chat_called",
            model=selected_model,
            message_count=len(messages),
            temperature=temperature,
            max_tokens=max_tokens,
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
                "Mock HuggingFace chat response for: "
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
        return {
            "provider": self.provider_name,
            "status": "available",
            "mode": "mock",
            "default_model": self.default_model,
        }