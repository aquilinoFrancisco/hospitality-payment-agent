# app/api/routes.py
"""
REST API routes for the Hospitality Reservation Payment Agent.

This layer exposes simple REST endpoints for the MVP.
Business logic stays in services and repositories.
Payment execution is not performed here.
"""

from __future__ import annotations

from typing import Any, Dict

import structlog
from fastapi import APIRouter, HTTPException

from agent_mcp.server import MCPServer
from rag.retriever import retrieve_relevant_policies

logger = structlog.get_logger()

router = APIRouter()


@router.get("/rooms")
async def list_rooms() -> Dict[str, Any]:
    """
    List available demo rooms.

    Returns:
        JSON-safe room catalog.
    """
    return {
        "rooms": [
            {
                "id": "deluxe-suite",
                "name": "Deluxe Suite",
                "base_price": 250.00,
                "capacity": 3,
            },
            {
                "id": "standard-queen",
                "name": "Standard Queen Room",
                "base_price": 140.00,
                "capacity": 2,
            },
            {
                "id": "penthouse",
                "name": "Panoramic Penthouse",
                "base_price": 600.00,
                "capacity": 5,
            },
        ]
    }


@router.get("/reservations/{reservation_id}")
async def get_reservation(reservation_id: str) -> Dict[str, Any]:
    """
    Get reservation detail and status.

    MVP:
        Returns a mock reservation response.

    Future:
        Read from reservation repository.
    """
    logger.info(
        "get_reservation_requested",
        reservation_id=reservation_id,
    )

    return {
        "reservation_id": reservation_id,
        "customer_email": "aquilino.francisco@gmail.com",
        "room_type": "deluxe-suite",
        "status": "PENDING_PAYMENT",
        "payment_link": (
            f"https://checkout.stripe.com/pay/mock_session_{reservation_id}"
        ),
        "total_price": 500.00,
        "currency": "USD",
        "idempotency_key": "idem_key_abc123",
    }


@router.post("/reserve")
async def create_reservation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a reservation MVP flow.

    This endpoint uses MCP tools only.

    Expected payload:
        {
            "customer_id": "CUST-001",
            "room_id": "deluxe-suite",
            "check_in": "2026-08-10",
            "check_out": "2026-08-12",
            "guests": 2
        }
    """
    logger.info(
        "create_reservation_requested",
        payload=payload,
    )

    required_fields = [
        "customer_id",
        "room_id",
        "check_in",
        "check_out",
        "guests",
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in payload
    ]

    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Missing required fields",
                "missing_fields": missing_fields,
            },
        )

    server = MCPServer()

    availability = server.call_tool(
        "check_availability",
        room_id=payload["room_id"],
        check_in=payload["check_in"],
        check_out=payload["check_out"],
    )

    if not availability.get("available", False):
        return {
            "status": "ROOM_NOT_AVAILABLE",
            "availability": availability,
        }

    pricing = server.call_tool(
        "calculate_price",
        room_id=payload["room_id"],
        check_in=payload["check_in"],
        check_out=payload["check_out"],
        guests=payload["guests"],
    )

    reservation_id = payload.get(
        "reservation_id",
        "RES-MVP-001",
    )

    payment = server.call_tool(
        "create_payment_link",
        reservation_id=reservation_id,
        amount=pricing.get("total_price", 0),
        currency=pricing.get("currency", "USD"),
    )

    policies = retrieve_relevant_policies(
        query="payment cancellation refund hotel terms",
        limit=2,
    )

    return {
        "status": "PENDING_PAYMENT",
        "reservation_id": reservation_id,
        "customer_id": payload["customer_id"],
        "room_id": payload["room_id"],
        "availability": availability,
        "pricing": pricing,
        "payment": payment,
        "policy_context": policies,
        "safety_rule": (
            "The agent never charges directly. "
            "The customer must complete payment through Stripe Sandbox."
        ),
    }


@router.get("/policies/search")
async def search_policies(query: str) -> Dict[str, Any]:
    """
    Search hotel policies using the local RAG retriever.
    """
    results = retrieve_relevant_policies(
        query=query,
        limit=3,
    )

    return {
        "query": query,
        "results": results,
    }


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Basic API health check.
    """
    return {
        "status": "ok",
        "service": "hospitality-reservation-payment-agent",
    }