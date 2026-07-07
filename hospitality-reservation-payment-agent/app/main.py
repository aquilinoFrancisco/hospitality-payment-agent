# app/main.py
"""
FastAPI application entrypoint.

This API exposes:

- REST reservation endpoints
- Server-Sent Events (SSE) reservation streaming
- Multi-provider payment webhooks
- Provider-agnostic payment architecture

Current architecture:

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
Payment Provider Factory
    ↓
Stripe / Conekta / Mercado Pago
"""

from __future__ import annotations

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.api.stream import router as stream_router
from app.api.webhooks import router as webhook_router

logger = structlog.get_logger()

APP_VERSION = "1.0.0"

app = FastAPI(
    title="Hospitality Reservation Payment Agent",
    description=(
        "AI Agent Platform for hospitality reservations using "
        "FastAPI, LangGraph, CrewAI, MCP Tools, Local RAG and "
        "a provider-agnostic payment architecture."
    ),
    version=APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# REST API
# ------------------------------------------------------------------

app.include_router(
    api_router,
    prefix="/api",
    tags=["API"],
)

# ------------------------------------------------------------------
# Streaming API (SSE)
# ------------------------------------------------------------------

app.include_router(
    stream_router,
    tags=["Streaming"],
)

# ------------------------------------------------------------------
# Payment Webhooks
# ------------------------------------------------------------------

app.include_router(
    webhook_router,
    prefix="/webhooks",
    tags=["Payment Webhooks"],
)


@app.on_event("startup")
async def startup_event() -> None:
    """
    Application startup.
    """

    logger.info(
        "application_starting",
        service="hospitality-reservation-payment-agent",
        version=APP_VERSION,
        mode="mvp",
        architecture="provider-agnostic",
    )


@app.get("/health")
async def health_check() -> dict:
    """
    Health endpoint.

    Useful for:
    - Kubernetes
    - Docker
    - Azure App Service
    - AWS ECS
    - Cloud Run
    - Monitoring systems
    """

    return {
        "status": "healthy",
        "service": "hospitality-reservation-payment-agent",
        "version": APP_VERSION,
        "architecture": "provider-agnostic",
        "payment_providers": [
            "stripe",
            "conekta",
            "mercado_pago",
        ],
        "capabilities": [
            "FastAPI",
            "LangGraph Workflow",
            "CrewAI Agents",
            "MCP Tools",
            "Local RAG",
            "Server Sent Events",
            "Multi-provider Payments",
            "Webhook Confirmation",
            "Repository Pattern",
            "Service Layer",
        ],
        "configuration": {
            "payment_provider": "configurable",
            "currency": "configurable",
            "country": "configurable",
            "llm_provider": "configurable",
            "embedding_provider": "configurable",
        },
    }