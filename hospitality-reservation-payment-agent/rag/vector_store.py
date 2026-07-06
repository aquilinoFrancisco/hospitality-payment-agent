# rag/vector_store.py
class SimpleVectorStore:
    """Simple in-memory semantic database for policies."""
    def __init__(self):
        self.documents = []
    def add_document(self, doc_id: str, content: str, embedding: list):
        self.documents.append({"id": doc_id, "content": content, "embedding": embedding})
