# Architecture Overview

This portfolio showcases an **AI Agentic platform** designed to solve hotel reservations and secure payments with a safe, fully-auditable sandbox workflow.

## Component Stack
- **FastAPI**: Gateway microservice serving REST APIs, webhook receivers, and real-time Server-Sent Events (SSE) updates.
- **Services Layer**: Framework-agnostic pure business logic for core reservations and payment workflows (`reservation_service.py`, `payment_service.py`). Manages state-machine transitions and pricing.
- **Repositories Layer**: Pure data access layer reading and writing JSON files (`room_repository.py`, `customer_repository.py`, `reservation_repository.py`, `payment_repository.py`). Strictly decoupled from business logic and state machine mechanics.
- **Integrations Layer**: Safe sandbox API client wrappers (such as Stripe Sandbox wrappers) with zero hardcoded credentials or initialization side-effects.
- **Core Package**: Application config parsing and structured logging setups.
- **LangGraph**: Workflow engine routing state validations, room scheduling checks, and price calculators.
- **CrewAI**: Orchestrator containing two specialized task agents: `ReservationAgent` and `PaymentAgent`.
- **MCP-Style Tools**: Encapsulated system interfaces exposing database actions, price calculations, and checkout sessions to agents.
- **Local RAG**: Context-aware retrieval engine that injects hotel reservation, refund, and cancellation policies into the workflow.
