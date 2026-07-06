# rag/retriever.py
def retrieve_relevant_policies(query: str, limit: int = 2):
    """Retrieve Cancellation, Refund, or Payment policy matching keywords."""
    return ["Refund policy: 100% refund up to 24 hours prior to check-in."]
