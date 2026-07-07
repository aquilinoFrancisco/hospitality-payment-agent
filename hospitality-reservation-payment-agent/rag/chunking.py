# rag/chunking.py
"""
Chunking utilities for Local RAG.

This module keeps backward compatibility with the original
split_markdown_into_chunks() function while introducing a cleaner
architecture-ready chunking strategy.

Architecture:

Document Loader
        ↓
Chunking Strategy
        ↓
Embedding Router
        ↓
Vector Store Router
        ↓
Retriever
        ↓
LLM Router
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List
import uuid


@dataclass
class Chunk:
    """
    Normalized document chunk.
    """

    chunk_id: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ChunkingStrategy(ABC):
    """
    Abstract base class for chunking strategies.
    """

    strategy_name: str

    @abstractmethod
    def chunk(
        self,
        text: str,
        metadata: Dict[str, Any] | None = None,
    ) -> List[Chunk]:
        """
        Split text into normalized chunks.
        """
        raise NotImplementedError


class RecursiveChunker(ChunkingStrategy):
    """
    MVP recursive chunker.

    Strategy:
    - Keep paragraphs together whenever possible.
    - Split oversized paragraphs only when necessary.
    - Preserve metadata.
    - Add deterministic chunk order.
    """

    strategy_name = "recursive"

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 0,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")

        if overlap < 0:
            raise ValueError("overlap must be zero or greater.")

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size.")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(
        self,
        text: str,
        metadata: Dict[str, Any] | None = None,
    ) -> List[Chunk]:
        metadata = metadata or {}

        raw_chunks = split_markdown_into_chunks(
            text=text,
            chunk_size=self.chunk_size,
            overlap=self.overlap,
        )

        chunks: List[Chunk] = []

        for index, chunk_text in enumerate(raw_chunks):
            chunks.append(
                Chunk(
                    chunk_id=metadata.get(
                        "document_id",
                        str(uuid.uuid4()),
                    )
                    + f"::chunk_{index}",
                    text=chunk_text,
                    metadata={
                        **metadata,
                        "chunk_index": index,
                        "chunk_size": self.chunk_size,
                        "overlap": self.overlap,
                        "chunking_strategy": self.strategy_name,
                    },
                )
            )

        return chunks


def split_markdown_into_chunks(
    text: str,
    chunk_size: int = 500,
    overlap: int = 0,
) -> list[str]:
    """
    Split Markdown text into clean chunks.

    Backward-compatible utility function.

    Strategy:
    - Keep paragraphs together.
    - Split oversized paragraphs only when necessary.
    - Ignore empty blocks.
    - Optionally apply overlap to oversized paragraph splits.

    Args:
        text: Markdown document.
        chunk_size: Maximum characters per chunk.
        overlap: Number of characters to overlap between oversized splits.

    Returns:
        List of text chunks.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0:
        raise ValueError("overlap must be zero or greater.")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    chunks: list[str] = []

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    step = chunk_size - overlap

    for paragraph in paragraphs:
        if len(paragraph) <= chunk_size:
            chunks.append(paragraph)
            continue

        for start in range(0, len(paragraph), step):
            chunk = paragraph[start:start + chunk_size].strip()

            if chunk:
                chunks.append(chunk)

    return chunks