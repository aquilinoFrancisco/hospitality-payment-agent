"""
LLM Integration Package.

This package provides a provider-agnostic abstraction for Large Language Models.

Current supported providers:
- Gemini (Mock)

Future providers:
- OpenAI
- Claude
- Llama
- Ollama
- Hugging Face

Architecture:

LangGraph
      │
CrewAI
      │
LLMProviderFactory
      │
 ┌────┼───────────────────────────┐
 ▼    ▼        ▼        ▼         ▼
Gemini OpenAI Claude  Llama   Ollama

Business logic never communicates directly with any LLM SDK.
All provider selection is centralized through LLMProviderFactory.
"""

from integrations.llm.base import LLMProvider
from integrations.llm.factory import LLMProviderFactory
from integrations.llm.gemini_provider import GeminiProvider

__all__ = [
    "LLMProvider",
    "LLMProviderFactory",
    "GeminiProvider",
]