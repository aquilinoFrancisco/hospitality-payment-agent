"""
Simple Markdown chunking utilities.

This MVP implementation keeps paragraphs together whenever possible,
producing cleaner chunks for embedding generation.
"""


def split_markdown_into_chunks(
    text: str,
    chunk_size: int = 500,
) -> list[str]:
    """
    Split Markdown text into semantic chunks.

    Strategy:
    - Keep paragraphs together.
    - Split oversized paragraphs only when necessary.
    - Ignore empty blocks.

    Args:
        text: Markdown document.
        chunk_size: Maximum characters per chunk.

    Returns:
        List of text chunks.
    """

    chunks = []

    paragraphs = [
        p.strip()
        for p in text.split("\n\n")
        if p.strip()
    ]

    for paragraph in paragraphs:

        if len(paragraph) <= chunk_size:
            chunks.append(paragraph)
            continue

        for i in range(0, len(paragraph), chunk_size):
            chunks.append(
                paragraph[i:i + chunk_size]
            )

    return chunks