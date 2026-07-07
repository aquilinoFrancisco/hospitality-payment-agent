# hospitality-reservation-payment-agent/core/config.py
"""
Application configuration.

This module centralizes all configurable values for the platform.

Design principles:
- No hardcoded payment provider logic.
- No hardcoded LLM provider logic.
- No hardcoded embedding provider logic.
- Environment-driven configuration.
- Safe defaults for local development.
- Providers can change without modifying LangGraph, CrewAI, MCP tools,
  services or repositories.
"""

from __future__ import annotations

import os

from pydantic import BaseModel


class Settings(BaseModel):
    """
    Central application settings.

    The objective is to make the platform configurable without changing
    the business workflow.
    """

    # ---------------------------------------------------------
    # Application
    # ---------------------------------------------------------

    APP_NAME: str = "Hospitality Reservation Payment Agent"
    ENV: str = os.getenv("NODE_ENV", "development")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ---------------------------------------------------------
    # LLM configuration
    # ---------------------------------------------------------

    DEFAULT_LLM_PROVIDER: str = os.getenv(
        "DEFAULT_LLM_PROVIDER",
        "gemini",
    )

    DEFAULT_LLM_MODEL: str = os.getenv(
        "DEFAULT_LLM_MODEL",
        "gemini-2.5-flash",
    )

    DEFAULT_LLM_TEMPERATURE: float = float(
        os.getenv(
            "DEFAULT_LLM_TEMPERATURE",
            "0.2",
        )
    )

    DEFAULT_LLM_MAX_TOKENS: int = int(
        os.getenv(
            "DEFAULT_LLM_MAX_TOKENS",
            "1024",
        )
    )

    SUPPORTED_LLM_PROVIDERS: list[str] = [
        "gemini",
        "openai",
        "claude",
        "llama",
        "ollama",
        "huggingface",
    ]

    # ---------------------------------------------------------
    # Embedding configuration
    # ---------------------------------------------------------

    DEFAULT_EMBEDDING_PROVIDER: str = os.getenv(
        "DEFAULT_EMBEDDING_PROVIDER",
        "mock",
    )

    DEFAULT_EMBEDDING_MODEL: str = os.getenv(
        "DEFAULT_EMBEDDING_MODEL",
        "mock-384",
    )

    DEFAULT_EMBEDDING_DIMENSIONS: int = int(
        os.getenv(
            "DEFAULT_EMBEDDING_DIMENSIONS",
            "384",
        )
    )

    SUPPORTED_EMBEDDING_PROVIDERS: list[str] = [
        "mock",
        "openai",
        "gemini",
        "huggingface",
        "voyage",
        "ollama",
    ]

    # ---------------------------------------------------------
    # AI provider credentials
    # ---------------------------------------------------------

    GEMINI_API_KEY: str = os.getenv(
        "GEMINI_API_KEY",
        "mock_gemini_key",
    )

    OPENAI_API_KEY: str = os.getenv(
        "OPENAI_API_KEY",
        "mock_openai_key",
    )

    ANTHROPIC_API_KEY: str = os.getenv(
        "ANTHROPIC_API_KEY",
        "mock_claude_key",
    )

    HUGGINGFACE_API_KEY: str = os.getenv(
        "HUGGINGFACE_API_KEY",
        "mock_huggingface_key",
    )

    OLLAMA_BASE_URL: str = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434",
    )

    VOYAGE_API_KEY: str = os.getenv(
        "VOYAGE_API_KEY",
        "mock_voyage_key",
    )

    # ---------------------------------------------------------
    # RAG / Vector store configuration
    # ---------------------------------------------------------

    VECTOR_STORE_PROVIDER: str = os.getenv(
        "VECTOR_STORE_PROVIDER",
        "memory",
    )

    SUPPORTED_VECTOR_STORES: list[str] = [
        "memory",
        "pgvector",
        "opensearch",
        "faiss",
        "pinecone",
    ]

    ENABLE_RAG: bool = (
        os.getenv("ENABLE_RAG", "true").lower() == "true"
    )

    # ---------------------------------------------------------
    # Payment provider configuration
    # ---------------------------------------------------------

    PAYMENT_PROVIDER_DEFAULT: str = os.getenv(
        "PAYMENT_PROVIDER_DEFAULT",
        "stripe",
    )

    SUPPORTED_PAYMENT_PROVIDERS: list[str] = [
        "stripe",
        "conekta",
        "mercado_pago",
    ]

    # ---------------------------------------------------------
    # Currency configuration
    # ---------------------------------------------------------

    DEFAULT_COUNTRY: str = os.getenv(
        "DEFAULT_COUNTRY",
        "MX",
    )

    DEFAULT_CURRENCY: str = os.getenv(
        "DEFAULT_CURRENCY",
        "mxn",
    )

    SUPPORTED_CURRENCIES: list[str] = [
        "mxn",
        "usd",
        "eur",
        "ars",
        "brl",
        "cop",
        "clp",
    ]

    COUNTRY_PAYMENT_PROVIDER: dict[str, str] = {
        "MX": "conekta",
        "US": "stripe",
        "ES": "stripe",
        "AR": "mercado_pago",
        "BR": "mercado_pago",
        "CO": "mercado_pago",
        "CL": "mercado_pago",
    }

    COUNTRY_DEFAULT_CURRENCY: dict[str, str] = {
        "MX": "mxn",
        "US": "usd",
        "ES": "eur",
        "AR": "ars",
        "BR": "brl",
        "CO": "cop",
        "CL": "clp",
    }

    # ---------------------------------------------------------
    # Stripe
    # ---------------------------------------------------------

    STRIPE_SECRET_KEY: str = os.getenv(
        "STRIPE_SECRET_KEY",
        "mock_stripe_key",
    )

    STRIPE_WEBHOOK_SECRET: str = os.getenv(
        "STRIPE_WEBHOOK_SECRET",
        "mock_webhook_secret",
    )

    # ---------------------------------------------------------
    # Conekta
    # ---------------------------------------------------------

    CONEKTA_PRIVATE_KEY: str = os.getenv(
        "CONEKTA_PRIVATE_KEY",
        "mock_conekta_key",
    )

    CONEKTA_WEBHOOK_SECRET: str = os.getenv(
        "CONEKTA_WEBHOOK_SECRET",
        "mock_conekta_webhook",
    )

    # ---------------------------------------------------------
    # Mercado Pago
    # ---------------------------------------------------------

    MERCADO_PAGO_ACCESS_TOKEN: str = os.getenv(
        "MERCADO_PAGO_ACCESS_TOKEN",
        "mock_mp_token",
    )

    MERCADO_PAGO_WEBHOOK_SECRET: str = os.getenv(
        "MERCADO_PAGO_WEBHOOK_SECRET",
        "mock_mp_webhook",
    )

    # ---------------------------------------------------------
    # Future integrations
    # ---------------------------------------------------------

    ENABLE_NOTIFICATIONS: bool = (
        os.getenv("ENABLE_NOTIFICATIONS", "false").lower() == "true"
    )

    # ---------------------------------------------------------
    # Helper methods
    # ---------------------------------------------------------

    def get_provider_for_country(self, country_code: str | None = None) -> str:
        """
        Return the preferred payment provider for a country.
        """
        country = (country_code or self.DEFAULT_COUNTRY).upper()

        return self.COUNTRY_PAYMENT_PROVIDER.get(
            country,
            self.PAYMENT_PROVIDER_DEFAULT,
        )

    def get_currency_for_country(self, country_code: str | None = None) -> str:
        """
        Return the default currency for a country.
        """
        country = (country_code or self.DEFAULT_COUNTRY).upper()

        return self.COUNTRY_DEFAULT_CURRENCY.get(
            country,
            self.DEFAULT_CURRENCY,
        )

    def is_supported_llm_provider(
        self,
        provider: str,
    ) -> bool:
        """
        Validate whether an LLM provider is supported.
        """
        return provider.lower().strip() in self.SUPPORTED_LLM_PROVIDERS

    def get_default_llm_provider(self) -> str:
        """
        Return the configured default LLM provider.
        """
        return self.DEFAULT_LLM_PROVIDER

    def get_default_llm_model(self) -> str:
        """
        Return the configured default LLM model.
        """
        return self.DEFAULT_LLM_MODEL

    def is_supported_embedding_provider(
        self,
        provider: str,
    ) -> bool:
        """
        Validate whether an embedding provider is supported.
        """
        return provider.lower().strip() in self.SUPPORTED_EMBEDDING_PROVIDERS

    def get_default_embedding_provider(self) -> str:
        """
        Return the configured default embedding provider.
        """
        return self.DEFAULT_EMBEDDING_PROVIDER

    def get_default_embedding_model(self) -> str:
        """
        Return the configured default embedding model.
        """
        return self.DEFAULT_EMBEDDING_MODEL

    def get_default_embedding_dimensions(self) -> int:
        """
        Return the configured embedding dimensions.
        """
        return self.DEFAULT_EMBEDDING_DIMENSIONS


settings = Settings()