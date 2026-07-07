# integrations/llm/ollama_provider.py
"""
Ollama LLM Provider.

Current MVP:
- Mock implementation
- No real Ollama API call
- No local model required

Future:
- Connect to a local Ollama server (http://localhost:11434)
- Support local models such as:
    - llama3
    - mistral
    - qwen
    - phi3
    - gemma

Purpose:
This provider enables on-premise and privacy-first deployments while
conforming to the common LLMProvider contract.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog

from integrations.llm.base import LLMProvider

logger = structlog.get_logger()


class OllamaProvider(LLMProvider):
    """
    Ollama implementation of the LLMProvider contract.
    """

    provider_name = "ollama"
    default_model = "llama3.2"

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
            "ollama_generate_called",
            model=selected_model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return {
            "provider": self.provider_name,
            "model": selected_model,
            "mode": "mock",
            "content": (
                "Mock Ollama response. Replace this implementation with "
                "a real Ollama REST API call."
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
            "ollama_chat_called",
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
                "Mock Ollama chat response for: "
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