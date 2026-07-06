# System Design Interview Prep

This repository is optimized for technical system design demonstrations:

### Key Talking Points:
1. **Security**: Zero access to credit card detail inside the LLM prompt. Exclusively handles tokenized Sandbox session IDs.
2. **Idempotency**: How Stripe idempotency keys protect the system from network retry issues.
3. **State Consistency**: Decoupled REST routes where state can only transition to `PAID` via webhook signatures.
4. **Agent-Tool Separation**: Decoupling tool logical implementations using MCP servers.
