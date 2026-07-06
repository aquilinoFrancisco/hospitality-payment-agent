# app/main.py
"""
FastAPI application entrypoint.

This API exposes:
- REST reservation endpoints
- Server-Sent Events reservation streaming
- Stripe webhook placeholder endpoints
"""

from __future__ import annotations

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.api.stream import router as stream_router
from app.api.webhooks import router as webhook_router

logger = structlog.get_logger()

app = FastAPI(
    title="Hospitality Reservation Payment Agent",
    description=(
        "AI agentic platform for hotel reservations, safe payment-link "
        "generation, local RAG policies, MCP-style tools, and SSE streaming."
    ),
    version="0.8.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API
app.include_router(
    api_router,
    prefix="/api",
    tags=["api"],
)

# SSE streaming API
app.include_router(
    stream_router,
    tags=["streaming"],
)

# Stripe webhook placeholder
app.include_router(
    webhook_router,
    prefix="/webhooks",
    tags=["webhooks"],
)


@app.on_event("startup")
async def startup_event() -> None:
    """
    Application startup hook.
    """
    logger.info(
        "application_starting",
        service="hospitality-reservation-payment-agent",
        version="0.8.0",
        mode="mvp",
    )


@app.get("/health")
async def health_check() -> dict:
    """
    Root health check.
    """
    return {
        "status": "healthy",
        "service": "hospitality-reservation-payment-agent",
        "version": "0.8.0",
        "capabilities": [
            "FastAPI",
            "MCP-style tools",
            "LangGraph-ready workflow",
            "CrewAI-ready agents",
            "Local RAG policies",
            "SSE streaming",
            "Stripe Sandbox-ready payments",
        ],
    }