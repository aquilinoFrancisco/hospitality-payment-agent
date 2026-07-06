# rag/chunking.py
def split_markdown_into_chunks(text: str, chunk_size: int = 500) -> list:
    """Helper to slice policy markdown files into readable embedding passages."""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
