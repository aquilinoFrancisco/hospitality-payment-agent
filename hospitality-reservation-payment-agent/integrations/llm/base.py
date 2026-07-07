# integrations/llm/base.py
"""
Base contract for LLM providers.

This abstraction allows the platform to switch between Gemini, OpenAI,
Claude, Llama, Ollama or any future LLM provider without changing the
business workflow.

Business rule:
LangGraph, CrewAI and services should not depend directly on a specific
LLM SDK. They should depend on this contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class LLMProvider(ABC):
    """
    Common interface for all LLM providers.
    """

    provider_name: str
    default_model: str

    @abstractmethod
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
        Generate a single response from the selected LLM provider.
        """
        raise NotImplementedError

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a chat response from a list of messages.

        Expected message format:
            [
                {"role": "system", "content": "..."},
                {"role": "user", "content": "..."}
            ]
        """
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Return provider health information.
        """
        raise NotImplementedError