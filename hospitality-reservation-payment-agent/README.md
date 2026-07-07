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

The AI agent never charges customers 

___

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
        ┌──────────────┼──────────────────────┐
        ▼              ▼                      ▼
 Local RAG     Payment Provider Factory   LLM Provider Factory
        │              │                      │
        │      ┌───────┼──────────────┐       ├───────────────┬───────────────┬──────────────┬──────────────┬──────────────┐
        │      ▼       ▼              ▼       ▼               ▼               ▼              ▼              ▼
        │   Stripe  Conekta    Mercado Pago Gemini         OpenAI         Claude         Llama        Ollama   HuggingFace
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
- LLM Provider Factory
- Mock LLM Providers

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