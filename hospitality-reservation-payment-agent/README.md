# Hospitality Reservation Payment Agent

## Overview

Hospitality Reservation Payment Agent is an AI Agent platform demonstrating a modern, event-driven reservation workflow for hotels.

The project showcases how LangGraph, CrewAI, MCP Tools, FastAPI, Local RAG and multiple payment providers can be combined into a modular, auditable and production-ready architecture.

The project is intentionally implemented as an MVP using mock data while preserving enterprise architecture patterns.

---

# Business Goal

Build an AI Agent platform capable of:

- Validating reservation requests
- Checking room availability
- Calculating reservation pricing
- Consulting hotel policies using Local RAG
- Generating secure payment links
- Supporting multiple payment providers
- Receiving webhook confirmations
- Maintaining a fully auditable workflow

The AI agent never charges customers directly.

---

# Architecture

```text
                Client
                   │
                   ▼
              FastAPI API
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   REST Endpoints        SSE Streaming
        │                     │
        └──────────┬──────────┘
                   ▼
              LangGraph
                   │
                   ▼
               CrewAI Crew
                   │
                   ▼
              MCP Tool Server
                   │
                   ▼
            Business Services
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
      Local RAG      Payment Providers
                              │
             ┌────────────────┼───────────────┐
             ▼                ▼               ▼
          Stripe          Conekta      Mercado Pago
```

---

# Technology Stack

- Python 3.11
- FastAPI
- LangGraph
- CrewAI
- MCP-style Tools
- Local RAG
- Mock JSON Repository
- Structured Logging
- Stripe Sandbox
- Conekta Sandbox
- Mercado Pago Sandbox

Architecture prepared for:

- OpenAI
- Claude
- Gemini
- Llama
- HuggingFace
- Ollama
- Voyage AI

---

# Main Features

- AI Reservation Workflow
- Multi-step LangGraph orchestration
- CrewAI collaborative agents
- Local RAG policy retrieval
- Provider-agnostic payment architecture
- Multi-country payment configuration
- Idempotent payment operations
- Webhook-driven state transitions
- Structured logging
- Repository pattern
- Service layer
- MCP Tool abstraction

---

# Current Workflow

```text
Reservation Request
        │
        ▼
Validate Request
        ▼
Check Availability
        ▼
Calculate Price
        ▼
Retrieve Hotel Policies (RAG)
        ▼
Reservation Agent
        ▼
Payment Agent
        ▼
Generate Payment Link
        ▼
Customer Payment
        ▼
Webhook
        ▼
Reservation Confirmed
```

---

# Project Structure

```text
app/
graph/
crew/
agent_mcp/
services/
repositories/
integrations/
rag/
knowledge_base/
mock_data/
docs/
tests/
```

---

# Documentation

Detailed documentation is available under the `docs/` directory.

- architecture.md
- payment-flow.md
- langgraph.md
- rag.md
- mcp.md
- interview-notes.md

---

# Current Status

Current implementation includes:

- Mock reservation workflow
- Local JSON repositories
- LangGraph orchestration
- CrewAI agents
- MCP tools
- Multi-provider payment abstraction
- Stripe Sandbox integration
- Conekta-ready architecture
- Mercado Pago-ready architecture
- Local RAG
- Structured logging

---

# Future Roadmap

Upcoming iterations will include:

- LLM Provider Factory
- Embedding Provider Factory
- Vector Store Factory
- Dynamic LangGraph routing
- Notification Agent
- Email integration
- WhatsApp integration
- SMS integration
- CRM integration
- Housekeeping integration
- Invoice generation
- Production payment gateways

---

# Design Principles

- Separation of Concerns
- Provider Agnostic Architecture
- Event-Driven Design
- Repository Pattern
- Service Layer
- Dependency Inversion
- Human-in-the-Loop
- Webhooks as Source of Truth
- Full Auditability
- Extensibility First