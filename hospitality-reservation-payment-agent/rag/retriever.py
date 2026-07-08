# rag/retriever.py
"""
RAG Retriever.

This module orchestrates the Local RAG retrieval flow using the new
provider-agnostic architecture.

Architecture:

Document / Query
        ↓
Chunking
        ↓
Embedding Router
        ↓
Vector Store Router
        ↓
Retrieved Context
        ↓
LLM Router / Agent Workflow

This file should not know specific embedding providers or vector databases.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog

from rag.chunking import RecursiveChunker
from rag.embeddings import get_text_embedding
from rag.vector_store import get_vector_store

logger = structlog.get_logger()


class RAGRetriever:
    """
    Provider-agnostic RAG retriever.

    Responsibilities:
    - Chunk documents.
    - Generate embeddings.
    - Store embedded chunks.
    - Retrieve relevant context for a query.

    It does not call OpenAI, Gemini, FAISS, PGVector, OpenSearch or Pinecone
    directly. Those decisions are delegated to the EmbeddingRouter and
    VectorStoreRouter through the RAG wrappers.
    """

    def __init__(
        self,
        embedding_provider: Optional[str] = None,
        embedding_model: Optional[str] = None,
        vector_store_provider: Optional[str] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.embedding_model = embedding_model

        self.vector_store = get_vector_store(
            provider=vector_store_provider,
        )

        self.chunker = RecursiveChunker(
            chunk_size=chunk_size,
            overlap=chunk_overlap,
        )

    def index_document(
        self,
        document_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Chunk, embed and index a document.
        """

        metadata = metadata or {}

        chunks = self.chunker.chunk(
            text=text,
            metadata={
                **metadata,
                "document_id": document_id,
            },
        )

        indexed_chunks = 0

        for chunk in chunks:
            embedding = get_text_embedding(
                text=chunk.text,
                provider=self.embedding_provider,
                model=self.embedding_model,
            )

            self.vector_store.add_document(
                doc_id=chunk.chunk_id,
                content=chunk.text,
                embedding=embedding,
                metadata=chunk.metadata,
            )

            indexed_chunks += 1

        logger.info(
            "rag_document_indexed",
            document_id=document_id,
            chunk_count=indexed_chunks,
        )

        return {
            "status": "success",
            "document_id": document_id,
            "chunk_count": indexed_chunks,
            "chunking_strategy": self.chunker.strategy_name,
        }

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a user query.
        """

        query_embedding = get_text_embedding(
            text=query,
            provider=self.embedding_provider,
            model=self.embedding_model,
        )

        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters,
        )

        logger.info(
            "rag_context_retrieved",
            query_length=len(query),
            top_k=top_k,
            results=len(results),
        )

        return results

    def retrieve_context(
        self,
        query: str,
        top_k: int = 3,
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Retrieve relevant chunks and return them as a single context string.
        """

        results = self.retrieve(
            query=query,
            top_k=top_k,
            filters=filters,
        )

        return "\n\n".join(
            result.get("content", "")
            for result in results
            if result.get("content")
        )

    def health_check(self) -> Dict[str, Any]:
        """
        Return RAG retriever health metadata.
        """

        return {
            "retriever": "rag_retriever",
            "chunking_strategy": self.chunker.strategy_name,
            "vector_store": self.vector_store.health_check(),
            "embedding_provider": self.embedding_provider or "default",
            "embedding_model": self.embedding_model or "default",
        }


def create_retriever(
    embedding_provider: Optional[str] = None,
    embedding_model: Optional[str] = None,
    vector_store_provider: Optional[str] = None,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> RAGRetriever:
    """
    Factory helper for creating a RAGRetriever.
    """

    return RAGRetriever(
        embedding_provider=embedding_provider,
        embedding_model=embedding_model,
        vector_store_provider=vector_store_provider,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )