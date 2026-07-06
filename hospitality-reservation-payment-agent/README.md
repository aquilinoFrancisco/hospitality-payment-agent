# Hospitality Reservation & Payment AI Agent Platform

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green.svg)](https://fastapi.tiangolo.com)
[![Stripe Sandbox](https://img.shields.io/badge/Stripe-Sandbox-635BFF.svg)](https://stripe.com)

An elegant agentic system engineered for **secured, auditable room reservation checkouts** using **LangGraph**, **CrewAI**, **MCP tools**, and **Stripe Sandbox integrations**.

> 💡 *Note: This repository is structured as a premium technical portfolio presentation for system design and advanced engineering showcases.*

## 🚀 Key Architectural Principles
- **Indirect Checkout Integration**: The conversational AI NEVER holds or requests primary cardholder numbers directly in raw inputs.
- **Strict Webhook Source of Truth**: State machine transitions are entirely driven by cryptographically-verified Stripe signature events (`checkout.session.completed`).
- **Decoupled Business Services**: Multi-Agent configurations invoke external actions through standard MCP (Model Context Protocol) specifications.
- **Idempotent Operations**: All workflows must provide unique idempotency keys before executing a sandbox transaction.

---

## 📂 Repository Layout
- `app/`: FastAPI controllers, routers, SSE endpoints, and webhooks.
- `services/`: Framework-agnostic pure business logic layer housing domain rules, validation, pricing calculators, and state machine transitions (`reservation_service.py`, `payment_service.py`).
- `repositories/`: Pure data access layer handling low-level loading and persistent serialization of JSON datasets under `mock_data/` (`room_repository.py`, `customer_repository.py`, `reservation_repository.py`, `payment_repository.py`). Strictly free of business rules.
- `integrations/`: Third-party integration packages (e.g., Stripe Sandbox API client).
- `core/`: Application settings, environment configuration, and structured logging.
- `graph/`: LangGraph definitions specifying state transitions and policy evaluations.
- `crew/`: CrewAI execution parameters (ReservationAgent & PaymentAgent specifications).
- `agent_mcp/`: Decoupled, fully implemented MCP Tools Layer (Phase 4 completed). Features `MCPServer` tool registry class and 8 structural business tools.
- `rag/`: semantic lookup module querying in-memory vectors.
- `knowledge_base/`: policy guidelines in pure markdown.
- `models/`: pydantic validation schemas.
- `mock_data/`: lightweight database presets.

---

## 💼 Business Domain & Workflow Lifecycles (Phase 2)

This system establishes a clean, framework-agnostic hotel booking and payment domain. All core processes are driven by deterministic state changes and decoupled business logic.

### 🏢 1. Core Business Entities
- **Room**: Represents lodging options (e.g., *Deluxe Suite*, *Panoramic Penthouse*). Includes properties for unique `id`, `name`, capacity, and daily `base_price`.
- **Customer**: Represents a customer account with their unique `id`, `name`, and contact `email`.
- **Reservation**: Connects a customer with a room type for a specified duration, capturing the active state machine status, total cost, metadata pointers (`idempotency_key`), and Stripe tracking parameters (`payment_link`, `payment_session_id`).
- **Payment**: Tracks transactional statuses (`PENDING`, `COMPLETED`, `REFUNDED`, `FAILED`) associated with Stripe Checkout sessions.

---

### 🔄 2. State Machine Lifecycle Transitions

The reservation flow is strictly guided through deterministic states to guarantee consistent audit trails:

```
  [REQUEST_RECEIVED]
          ↓
     [VALIDATED]
          ↓
[AVAILABILITY_CONFIRMED]
          ↓
  [PRICE_CALCULATED]
          ↓
   [PENDING_PAYMENT]   ───► [FAILED]
          ↓
        [PAID]         ───► [REFUNDED]
          ↓
[RESERVATION_CONFIRMED] ───► [CANCELLED]
```

#### Workflow States:
1. **`REQUEST_RECEIVED`**: Initial draft state when reservation request details are validated syntax-wise.
2. **`VALIDATED`**: The customer identity is authenticated and parameters are validated.
3. **`AVAILABILITY_CONFIRMED`**: Room calendars are checked and blocked to prevent double-booking.
4. **`PRICE_CALCULATED`**: Final pricing (base price × nights) and tax estimates are calculated.
5. **`PENDING_PAYMENT`**: A mock Stripe Checkout session is successfully registered and checkout link generated.
6. **`PAID`**: Payment verification callback/webhook receives completion signal from Stripe Sandbox.
7. **`RESERVATION_CONFIRMED`**: Room booking is finalized and locked into the customer schedule.
8. **`CANCELLED`**: Booking aborted prior to payment or by client cancellation.
9. **`REFUNDED`**: Payment successfully reverted, and reservation state updated to reflect the cancellation.
10. **`FAILED`**: Encountered an unexpected system, validation, or transaction error.

---

### 💳 3. Payment Lifecycle
- **`PENDING`**: Stripe session is initialized; waiting for customer to authorize charge.
- **`COMPLETED`**: Stripe webhook signals successful capture. Moves reservation status to `PAID` then immediately `RESERVATION_CONFIRMED`.
- **`REFUNDED`**: Administrator triggers standard charge refund, changing corresponding reservation status to `REFUNDED`.

---

### 🗄️ 4. Mock Data Strategy
To support offline development, testing, and rapid phone-based previews, we use an in-memory-first JSON database under `mock_data/`:
- **`rooms.json`**: Holds definitions for 10 realistic rooms.
- **`customers.json`**: Holds 5 standard customer accounts (including a standard portfolio recipient email).
- **`reservations.json`**: Tracks active reservation records and state progress.
- **`payments.json`**: Stores payments corresponding to booking checkout instances.
- **`availability.json`**: Date-by-date calendar blocks.

Every service query directly parses and persists updates to these files to guarantee real-time data consistency and high system fidelity without external database requirements.

---

---

## 🛠️ Step-by-Step Installation

### Prerequisites
- **Python 3.11+**
- **Docker** and **Docker-compose** (Optional)

### Local Configuration
1. Clone the repository:
   ```bash
   git clone https://github.com/aquilinoFrancisco/hospitality-reservation-payment-agent.git
   cd hospitality-reservation-payment-agent
   ```
2. Set up virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Set your credentials:
   ```bash
   cp .env.example .env
   # Modify values in .env safely
   ```
4. Start development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

---

## 🔗 Live Architecture Documentation
For deep-dives into each module's code structure and detailed system flowcharts:
- [Architecture Blueprint](./docs/architecture.md)
- [Stripe Sandbox Flow](./docs/payment-flow.md)
- [Model Context Protocol Integration](./docs/mcp.md)
- [Local RAG Design](./docs/rag.md)
- [LangGraph Routing Diagrams](./docs/langgraph.md)
- [System Design Interview Reference Sheets](./docs/interview-notes.md)
