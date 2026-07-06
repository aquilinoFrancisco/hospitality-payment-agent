# CrewAI Layer

## Overview

The CrewAI layer coordinates specialized AI agents responsible for different business capabilities within the hospitality reservation platform.

In this MVP, CrewAI is intentionally lightweight. The goal is to demonstrate a clean, modular architecture that can later be connected to production LLMs without changing the business logic.

---

# Architecture

```text
FastAPI
    ↓
LangGraph
    ↓
CrewAI
    ↓
MCP Tools
    ↓
Business Services
    ↓
Repositories
    ↓
Mock JSON
```

LangGraph orchestrates the workflow.

CrewAI coordinates specialized agents.

MCP Tools expose deterministic business capabilities.

Business Services implement business rules.

Repositories manage persistence.

---

# Agents

## ReservationAgent

### Responsibilities

- Validate reservation requests.
- Verify room availability.
- Review booking dates.
- Calculate reservation price.
- Prepare the reservation before payment.

The ReservationAgent never accesses repositories directly.

It only invokes MCP Tools.

---

## PaymentAgent

### Responsibilities

- Create Stripe Sandbox payment links.
- Verify payment status.
- Request refunds.
- Confirm reservations after payment.

The PaymentAgent never charges customers directly.

Payment execution always belongs to Stripe.

---

# Why CrewAI?

CrewAI allows each business responsibility to be isolated into a specialized agent.

Instead of creating one large AI assistant, the solution separates concerns into multiple focused agents.

Benefits:

- Better maintainability.
- Easier testing.
- Reusable agents.
- Clear business responsibilities.

---

# Why LangGraph + CrewAI?

LangGraph and CrewAI solve different problems.

## LangGraph

Responsible for:

- workflow orchestration;
- state management;
- conditional routing.

## CrewAI

Responsible for:

- specialized reasoning;
- task execution;
- collaboration between agents.

Together they provide a modular and production-oriented architecture.

---

# Payment Safety

The AI agent never performs financial transactions directly.

Safe payment flow:

```text
Reservation Request
        ↓
Availability Validation
        ↓
Price Calculation
        ↓
Create Payment Link
        ↓
Customer Pays
        ↓
Stripe Webhook
        ↓
Reservation Confirmed
```

The webhook is the source of truth.

Every payment operation includes an idempotency key.

---

# Future Production Evolution

The current MVP can evolve by adding:

- Real CrewAI execution.
- OpenAI or Anthropic models.
- Local RAG knowledge base.
- Stripe Sandbox integration.
- Server-Sent Events (SSE).
- Observability with LangSmith or Langfuse.
- PostgreSQL persistence.

The business architecture remains unchanged.

---

# Interview Summary

This project demonstrates how to build an AI Agent platform using:

- FastAPI
- LangGraph
- CrewAI
- MCP-style tools
- Clean Architecture
- Repository Pattern
- Business Services
- Stripe Sandbox
- Local RAG (planned)

The same architecture can be adapted to other domains such as:

- Retail operations
- Banking
- Insurance
- Healthcare
- Contract Intelligence
- Fraud Detection

Only the business domain, prompts, and tools change.