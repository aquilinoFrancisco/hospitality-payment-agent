# tests/test_rag_retriever.py
"""
Tests for RAGRetriever.

This validates the integrated RAG flow:

Document
    ↓
Chunking
    ↓
Embedding Router
    ↓
Vector Store Router
    ↓
Retrieved Context
"""

from rag.retriever import create_retriever


def test_rag_retriever_indexes_document_and_retrieves_context():
    retriever = create_retriever(
        embedding_provider="mock",
        embedding_model="mock-384",
        vector_store_provider="memory",
        chunk_size=120,
        chunk_overlap=20,
    )

    index_result = retriever.index_document(
        document_id="hotel_policy_001",
        text=(
            "Refunds are available up to 24 hours before check-in.\n\n"
            "Guests must present official identification at check-in.\n\n"
            "Payment links are generated securely by the payment provider."
        ),
        metadata={
            "source": "unit_test",
            "document_type": "hotel_policy",
        },
    )

    assert index_result["status"] == "success"
    assert index_result["document_id"] == "hotel_policy_001"
    assert index_result["chunk_count"] >= 1

    results = retriever.retrieve(
        query="What is the refund policy?",
        top_k=2,
    )

    assert isinstance(results, list)
    assert len(results) >= 1
    assert "content" in results[0]
    assert "score" in results[0]
    assert results[0]["metadata"]["source"] == "unit_test"


def test_rag_retriever_returns_context_string():
    retriever = create_retriever(
        embedding_provider="mock",
        embedding_model="mock-384",
        vector_store_provider="memory",
        chunk_size=120,
        chunk_overlap=20,
    )

    retriever.index_document(
        document_id="hotel_policy_002",
        text=(
            "Cancellation is allowed up to 48 hours before arrival.\n\n"
            "Late cancellation may generate a one-night charge."
        ),
        metadata={
            "source": "context_unit_test",
            "document_type": "hotel_policy",
        },
    )

    context = retriever.retrieve_context(
        query="Can a guest cancel the reservation?",
        top_k=2,
    )

    assert isinstance(context, str)
    assert len(context) > 0
    assert "Cancellation" in context or "cancellation" in context


def test_rag_retriever_health_check():
    retriever = create_retriever(
        embedding_provider="mock",
        embedding_model="mock-384",
        vector_store_provider="memory",
    )

    result = retriever.health_check()

    assert result["retriever"] == "rag_retriever"
    assert result["chunking_strategy"] == "recursive"
    assert result["vector_store"]["router"] == "vector_store_router"