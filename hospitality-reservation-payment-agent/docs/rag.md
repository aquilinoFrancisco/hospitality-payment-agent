# Local RAG Knowledge Retrieval

To make our reservation specialists compliant with legal guidelines and local policies, a lightweight Local RAG module (`rag/`) is integrated:

### Document Storage:
Policies in `knowledge_base/` are chunked and embedded:
- `cancellation_policy.md`
- `refund_policy.md`
- `payment_policy.md`
- `hotel_terms.md`

### Retrieval Flow:
Before calculating checkout parameters or deciding on cancellations, the system queries embeddings. The retrieved contextual passages are appended to the LangGraph/CrewAI context limits.
