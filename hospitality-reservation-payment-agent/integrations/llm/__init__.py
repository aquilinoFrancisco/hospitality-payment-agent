"""
LLM Integration Package.

This package provides a provider-agnostic abstraction layer for Large
Language Models (LLMs).

Supported providers:

- Gemini
- OpenAI
- Claude
- Llama
- Ollama
- HuggingFace

Architecture:

                    LangGraph
                        │
                        ▼
                    CrewAI Agents
                        │
                        ▼
                LLMProviderFactory
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
    Gemini          OpenAI          Claude
        │
        ├───────────────┬────────────────┐
        ▼               ▼                ▼
     Llama          Ollama        HuggingFace

Business rule:

Business workflows never communicate directly with any LLM SDK.

All LLM selection is centralized through the LLMProviderFactory,
making the platform vendor-agnostic and easy to extend.

Future providers can be added by implementing the LLMProvider contract
and registering the implementation in the factory.
"""

from integrations.llm.base import LLMProvider
from integrations.llm.factory import LLMProviderFactory
from integrations.llm.gemini_provider import GeminiProvider
from integrations.llm.openai_provider import OpenAIProvider
from integrations.llm.claude_provider import ClaudeProvider
from integrations.llm.llama_provider import LlamaProvider
from integrations.llm.ollama_provider import OllamaProvider
from integrations.llm.huggingface_provider import HuggingFaceProvider

__all__ = [
    "LLMProvider",
    "LLMProviderFactory",
    "GeminiProvider",
    "OpenAIProvider",
    "ClaudeProvider",
    "LlamaProvider",
    "OllamaProvider",
    "HuggingFaceProvider",
]