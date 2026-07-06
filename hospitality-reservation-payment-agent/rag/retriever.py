# rag/retriever.py
"""
Policy retriever for the Hospitality Reservation Payment Agent.

This module builds a small local RAG index from Markdown policy files.

Current MVP:
    - Reads Markdown files from knowledge_base/
    - Chunks policy documents
    - Generates deterministic mock embeddings
    - Stores vectors in memory
    - Retrieves relevant policy passages

Future production:
    - Replace vector store provider with PGVector, OpenSearch, FAISS or Pinecone
    - Replace mock embeddings with OpenAI, Azure OpenAI, Gemini or local models

The retriever depends only on the VectorStore interface.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from rag.chunking import split_markdown_into_chunks
from rag.embeddings import get_text_embedding
from rag.vector_store import VectorStore, get_vector_store


KNOWLEDGE_BASE_DIR = Path("knowledge_base")


def build_policy_index(
    knowledge_base_dir: Path = KNOWLEDGE_BASE_DIR,
    provider: str = "memory",
) -> VectorStore:
    """
    Build a policy vector index from Markdown files.

    Args:
        knowledge_base_dir:
            Directory containing policy Markdown files.
        provider:
            Vector store provider. Current MVP uses "memory".

    Returns:
        VectorStore instance populated with policy chunks.
    """

    vector_store = get_vector_store(provider)

    if not knowledge_base_dir.exists():
        return vector_store

    for policy_file in knowledge_base_dir.glob("*.md"):

        content = policy_file.read_text(
            encoding="utf-8"
        )

        chunks = split_markdown_into_chunks(content)

        for index, chunk in enumerate(chunks):

            doc_id = f"{policy_file.stem}-{index}"

            embedding = get_text_embedding(chunk)

            vector_store.add_document(
                doc_id=doc_id,
                content=chunk,
                embedding=embedding,
                metadata={
                    "source": policy_file.name,
                    "policy_type": policy_file.stem,
                    "chunk_index": index,
                },
            )

    return vector_store


def retrieve_relevant_policies(
    query: str,
    limit: int = 2,
    provider: str = "memory",
    filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant hotel policy passages.

    Args:
        query:
            User or agent query.
        limit:
            Maximum number of policy chunks to return.
        provider:
            Vector store provider.
        filters:
            Optional metadata filters.

    Returns:
        List of JSON-safe policy matches.
    """

    vector_store = build_policy_index(
        provider=provider
    )

    query_embedding = get_text_embedding(query)

    results = vector_store.search(
        query_embedding=query_embedding,
        top_k=limit,
        filters=filters,
    )

    return [
        {
            "content": result["content"],
            "source": result["metadata"].get("source"),
            "policy_type": result["metadata"].get("policy_type"),
            "score": result["score"],
        }
        for result in results
    ]


def retrieve_policy_context(
    query: str,
    limit: int = 2,
    provider: str = "memory",
) -> str:
    """
    Retrieve policy context as a formatted string for prompts.

    This is useful for CrewAI or LangGraph nodes that need simple text context.
    """

    policies = retrieve_relevant_policies(
        query=query,
        limit=limit,
        provider=provider,
    )

    if not policies:
        return "No relevant policy context found."

    context_blocks = []

    for policy in policies:

        context_blocks.append(
            f"Source: {policy['source']}\n"
            f"Policy Type: {policy['policy_type']}\n"
            f"Content: {policy['content']}"
        )

    return "\n\n---\n\n".join(context_blocks)