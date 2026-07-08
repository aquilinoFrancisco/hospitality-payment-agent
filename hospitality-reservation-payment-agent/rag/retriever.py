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
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import structlog

from rag.embeddings import get_text_embedding
from rag.vector_store import get_vector_store

logger = structlog.get_logger()


@dataclass
class DocumentChunk:
    """
    Normalized chunk representation used internally by the retriever.
    """

    chunk_id: str
    text: str
    metadata: Dict[str, Any]


class RAGRetriever:
    """
    Provider-agnostic RAG retriever.

    Responsibilities:
    - Chunk documents.
    - Generate embeddings.
    - Store embedded chunks.
    - Retrieve relevant context for a query.
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
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy_name = "recursive"

        self.vector_store = get_vector_store(
            provider=vector_store_provider,
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

        chunks = self._chunk_text(
            document_id=document_id,
            text=text,
            metadata=metadata,
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
            "chunking_strategy": self.strategy_name,
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
            "chunking_strategy": self.strategy_name,
            "vector_store": self.vector_store.health_check(),
            "embedding_provider": self.embedding_provider or "default",
            "embedding_model": self.embedding_model or "default",
        }

    def _chunk_text(
        self,
        document_id: str,
        text: str,
        metadata: Dict[str, Any],
    ) -> List[DocumentChunk]:
        """
        Lightweight recursive-style chunking.

        Keeps paragraphs together when possible and supports overlap.
        """

        if not text or not text.strip():
            return []

        paragraphs = [
            paragraph.strip()
            for paragraph in text.split("\n\n")
            if paragraph.strip()
        ]

        chunks: List[DocumentChunk] = []

        for paragraph in paragraphs:
            if len(paragraph) <= self.chunk_size:
                chunks.append(
                    self._build_chunk(
                        document_id=document_id,
                        text=paragraph,
                        metadata=metadata,
                        index=len(chunks),
                    )
                )
                continue

            start = 0
            step = max(1, self.chunk_size - self.chunk_overlap)

            while start < len(paragraph):
                end = start + self.chunk_size
                chunk_text = paragraph[start:end].strip()

                if chunk_text:
                    chunks.append(
                        self._build_chunk(
                            document_id=document_id,
                            text=chunk_text,
                            metadata=metadata,
                            index=len(chunks),
                        )
                    )

                start += step

        return chunks

    def _build_chunk(
        self,
        document_id: str,
        text: str,
        metadata: Dict[str, Any],
        index: int,
    ) -> DocumentChunk:
        """
        Build a normalized chunk object.
        """

        chunk_id = f"{document_id}_chunk_{index:04d}"

        return DocumentChunk(
            chunk_id=chunk_id,
            text=text,
            metadata={
                **metadata,
                "document_id": document_id,
                "chunk_id": chunk_id,
                "chunk_index": index,
            },
        )


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