# tests/test_embedding_router.py
"""
Tests for EmbeddingRouter.

These tests validate the minimum provider-agnostic embedding flow:

EmbeddingRouter
        ↓
EmbeddingProviderFactory
        ↓
MockEmbeddingProvider
"""

from integrations.embeddings import EmbeddingRouter


def test_embedding_router_generates_single_embedding():
    router = EmbeddingRouter(provider="mock", model="mock-384")

    result = router.generate_embedding(
        text="Refund policy allows cancellation up to 24 hours before check-in.",
        metadata={
            "source": "unit_test",
        },
    )

    assert result["provider"] == "mock"
    assert result["model"] == "mock-384"
    assert result["mode"] == "mock"
    assert isinstance(result["embedding"], list)
    assert result["dimensions"] == 384
    assert len(result["embedding"]) == 384
    assert result["metadata"]["source"] == "unit_test"


def test_embedding_router_generates_batch_embeddings():
    router = EmbeddingRouter(provider="mock", model="mock-384")

    result = router.generate_embeddings(
        texts=[
            "Cancellation policy.",
            "Payment policy.",
            "Refund policy.",
        ],
        metadata={
            "source": "batch_unit_test",
        },
    )

    assert result["provider"] == "mock"
    assert result["model"] == "mock-384"
    assert result["mode"] == "mock"
    assert isinstance(result["embeddings"], list)
    assert len(result["embeddings"]) == 3
    assert result["dimensions"] == 384
    assert result["metadata"]["source"] == "batch_unit_test"


def test_embedding_router_health_check():
    router = EmbeddingRouter(provider="mock", model="mock-384")

    result = router.health_check()

    assert result["router"] == "embedding_router"
    assert result["provider"] == "mock"
    assert result["model"] == "mock-384"
    assert result["provider_health"]["status"] == "available"