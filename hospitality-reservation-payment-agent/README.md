
# Hospitality Reservation Payment Agent

## A Provider-Agnostic Agentic AI Platform Reference Architecture

## Overview

Hospitality Reservation Payment Agent is a reference implementation of a modern **Provider-Agnostic Agentic AI Platform**.

Although the current business domain focuses on hotel reservations and payments, the architectural patterns are intentionally designed to be reusable across different enterprise AI solutions.

The platform demonstrates how modern AI orchestration frameworks can collaborate with traditional software engineering patterns to build scalable, maintainable, and auditable business systems.

Instead of tightly coupling the application to specific AI models, payment gateways, vector databases, or embedding providers, every external capability is abstracted through Routers and Factories.

This allows business workflows to remain stable while providers evolve independently.

Current implementation demonstrates:

- LangGraph as the decision engine
- CrewAI as domain specialists
- MCP Tools as controlled business capabilities
- Provider Routers for capability selection
- Provider Factories for implementation selection
- Local RAG for enterprise knowledge retrieval
- Repository + Service architecture
- Event-driven payment confirmation

The project is intentionally implemented as an MVP using mock providers while preserving enterprise architecture patterns.

---

# Architectural Principles

The platform follows four architectural principles.

### 1. LangGraph is the Decision Engine

LangGraph orchestrates the business workflow and decides what should happen next according to the current workflow state.

It never communicates directly with vendors.

---

### 2. Routers Select Capabilities

Routers determine which provider or capability should execute a specific task.

Examples:

- Payment Router
- LLM Router
- Embedding Router
- Vector Store Router

Routers isolate orchestration from implementation details.

---

### 3. Factories Instantiate Providers

Factories create the correct implementation without exposing vendor-specific SDKs to the business workflow.

Examples:

- Payment Provider Factory
- LLM Provider Factory
- Embedding Provider Factory
- Vector Store Factory

Adding a new provider becomes an extension instead of a rewrite.

---

### 4. Services Execute Business Rules

Business Services enforce domain rules, persistence, idempotency, and state transitions.

External providers never contain business logic.

---

# Business Goal

Build an AI Agent platform capable of:

- Validating reservation requests
- Checking room availability
- Calculating reservation pricing
- Consulting hotel policies using Local RAG
- Generating secure payment links
- Supporting multiple payment providers
- Supporting multiple LLM providers
- Supporting multiple embedding providers
- Supporting multiple vector stores
- Receiving webhook confirmations
- Maintaining a fully auditable workflow

The AI agent never charges customers directly.

It only orchestrates business capabilities through controlled MCP Tools.

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
             REST Endpoints       SSE Streaming
                  │                     │
                  └──────────┬──────────┘
                             ▼
                        LangGraph
                    (Decision Engine)
                             │
                             ▼
                     CrewAI Specialists
                             │
                             ▼
                       MCP Tool Server
                  (Controlled AI Actions)
                             │
                             ▼
                     Business Services
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
  Payment Router        LLM Router      VectorStore Router
        │                    │                    │
        ▼                    ▼                    ▼
Payment Provider      LLM Provider      VectorStore Factory
     Factory              Factory              │
        │                    │                 │
 ┌──────┼──────────┐     ┌────┼──────────────┐  ├──────────────┬──────────────┬──────────────┬──────────────┐
 ▼      ▼          ▼     ▼    ▼      ▼      ▼  ▼              ▼              ▼              ▼
Stripe Conekta Mercado Gemini OpenAI Claude Llama Memory      FAISS      PGVector   OpenSearch Pinecone
Pago                    Ollama HuggingFace
                             │
                             ▼
                    Embedding Router
                             │
                             ▼
                  Embedding Provider Factory
                             │
          ┌───────────┬────────────┬────────────┬────────────┐
          ▼           ▼            ▼            ▼
      OpenAI     HuggingFace    Gemini      Voyage AI
                                  │
                                  ▼
                               Ollama
```
# Project Structure

```text
hospitality-reservation-payment-agent/
│
├── app/                    # FastAPI application and API endpoints
│
├── graph/                  # LangGraph decision engine
│   ├── workflow.py
│   ├── state.py
│   ├── llm_router.py
│   └── prompts.py
│
├── crew/                   # CrewAI specialist agents
│
├── agent_mcp/              # MCP Tool Server
│   ├── server.py
│   └── tools/
│
├── services/               # Business services
│
├── repositories/           # Repository pattern
│
├── integrations/
│   │
│   ├── llm/
│   │   ├── router.py
│   │   ├── factory.py
│   │   ├── base.py
│   │   └── providers/
│   │
│   ├── payments/
│   │   ├── router.py
│   │   ├── factory.py
│   │   ├── base.py
│   │   └── providers/
│   │
│   ├── embeddings/         # (Roadmap)
│   │   ├── router.py
│   │   ├── factory.py
│   │   └── providers/
│   │
│   └── vector_store/       # (Roadmap)
│       ├── router.py
│       ├── factory.py
│       └── providers/
│
├── rag/                    # Retrieval-Augmented Generation
│
├── knowledge_base/         # Local knowledge base
│
├── mock_data/              # Mock repositories
│
├── docs/                   # Architecture documentation
│
└── tests/                  # Unit and integration tests
```

---

## Architectural Layers

```text
Presentation Layer
    └── FastAPI

Decision Layer
    ├── LangGraph
    └── CrewAI

Capability Layer
    ├── MCP Tools
    ├── Payment Router
    ├── LLM Router
    ├── Embedding Router (Roadmap)
    └── VectorStore Router (Roadmap)

Provider Layer
    ├── Payment Provider Factory
    ├── LLM Provider Factory
    ├── Embedding Provider Factory
    └── VectorStore Factory

Business Layer
    ├── Services
    └── Repositories

Knowledge Layer
    ├── Local RAG
    ├── Knowledge Base
    └── Mock Data
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

- LangGraph workflow orchestration
- CrewAI collaborative agents
- MCP Tool Server
- Provider-Agnostic Payment Factory
- Multi-provider payments (Stripe, Conekta, Mercado Pago)
- LLM Provider Factory
- Mock LLM Providers
  - Gemini
  - OpenAI
  - Claude
  - Llama
  - Ollama
  - HuggingFace
- Local RAG
- Repository Pattern
- Service Layer
- Structured Logging
- JSON Mock Repositories

---

# Future Roadmap

## AI Platform Evolution

- AI Provider Selection Engine
- Embedding Provider Factory
- Vector Store Factory

## Intelligent Orchestration

- Dynamic LangGraph Routing
- Multi-Agent Collaboration
- Event-Driven Workflows
- Human-in-the-Loop Approval

## Business Automation

- Notification Agent
- Email Integration
- WhatsApp Integration
- SMS Integration
- CRM Integration
- Housekeeping Integration
- Invoice Generation

## Enterprise Capabilities

- Multi-Tenant Architecture
- Observability Dashboard
- Analytics & Reporting
- Kubernetes Deployment
- CI/CD Pipeline

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