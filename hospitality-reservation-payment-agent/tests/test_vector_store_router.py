# tests/test_vector_store_router.py
"""
Tests for VectorStoreRouter.

These tests validate the provider-agnostic vector store flow:

VectorStoreRouter
        ↓
VectorStoreFactory
        ↓
Vector Store Providers
"""

from integrations.vector_store import VectorStoreRouter


def test_vector_store_router_health_check_memory():
    router = VectorStoreRouter(provider="memory")

    result = router.health_check()

    assert result["router"] == "vector_store_router"
    assert result["provider"] == "memory"
    assert result["provider_health"]["status"] == "available"


def test_vector_store_router_upserts_and_searches_documents():
    router = VectorStoreRouter(provider="memory")

    documents = [
        {
            "id": "doc_001",
            "text": "Refunds are available up to 24 hours before check-in.",
            "embedding": [0.1, 0.2, 0.3],
            "metadata": {
                "category": "refund",
            },
        },
        {
            "id": "doc_002",
            "text": "Guests must present identification at check-in.",
            "embedding": [0.9, 0.8, 0.7],
            "metadata": {
                "category": "check_in",
            },
        },
    ]

    upsert_result = router.upsert_documents(documents)

    assert upsert_result["provider"] == "memory"
    assert upsert_result["status"] == "success"
    assert upsert_result["upserted"] == 2

    search_result = router.similarity_search(
        query_embedding=[0.1, 0.2, 0.3],
        top_k=1,
    )

    assert search_result["provider"] == "memory"
    assert search_result["status"] == "success"
    assert len(search_result["results"]) == 1
    assert search_result["results"][0]["id"] == "doc_001"


def test_vector_store_router_applies_metadata_filters():
    router = VectorStoreRouter(provider="memory")

    documents = [
        {
            "id": "doc_refund",
            "text": "Refund policy.",
            "embedding": [0.1, 0.2, 0.3],
            "metadata": {
                "category": "refund",
            },
        },
        {
            "id": "doc_payment",
            "text": "Payment policy.",
            "embedding": [0.1, 0.2, 0.3],
            "metadata": {
                "category": "payment",
            },
        },
    ]

    router.upsert_documents(documents)

    result = router.similarity_search(
        query_embedding=[0.1, 0.2, 0.3],
        top_k=5,
        filters={
            "category": "payment",
        },
    )

    assert len(result["results"]) == 1
    assert result["results"][0]["id"] == "doc_payment"


def test_vector_store_router_supports_mock_provider_options():
    for provider in [
        "memory",
        "faiss",
        "pgvector",
        "opensearch",
        "pinecone",
    ]:
        router = VectorStoreRouter(provider=provider)
        result = router.health_check()

        assert result["provider"] == provider
        assert result["provider_health"]["status"] == "available"