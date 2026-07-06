"""
Application dependencies.

This module centralizes dependency injection for the Hospitality
Reservation Payment Agent.

Current MVP:
    • Mock persistence
    • Mock Stripe client
    • In-memory Vector Store

Future:
    • PostgreSQL
    • Redis
    • Stripe SDK
    • OpenSearch / PGVector
"""

from __future__ import annotations

import structlog

from rag.vector_store import get_vector_store

logger = structlog.get_logger()


# ==========================================================
# Database Dependency
# ==========================================================

async def get_db():
    """
    Mock database dependency.

    Future:
        Replace with PostgreSQL session.
    """

    logger.info("database_dependency_initialized")

    yield None


# ==========================================================
# Stripe Dependency
# ==========================================================

async def get_stripe_client():
    """
    Stripe dependency.

    MVP:
        Returns None.

    Future:

        import stripe

        stripe.api_key = ...

        yield stripe
    """

    logger.info("stripe_dependency_initialized")

    yield None


# ==========================================================
# Vector Store Dependency
# ==========================================================

def get_vector_store_dependency():
    """
    Return the configured Vector Store.

    Current:
        In-memory implementation.

    Future:
        provider="pgvector"
        provider="opensearch"
        provider="faiss"
        provider="pinecone"
    """

    logger.info(
        "vector_store_initialized",
        provider="memory",
    )

    return get_vector_store(
        provider="memory",
    )


# ==========================================================
# Application Configuration
# ==========================================================

def get_application_settings():
    """
    Central application configuration.

    Future:
        Replace with Pydantic Settings.
    """

    return {
        "environment": "development",
        "stripe_mode": "sandbox",
        "vector_store": "memory",
        "streaming": True,
        "rag_enabled": True,
    }