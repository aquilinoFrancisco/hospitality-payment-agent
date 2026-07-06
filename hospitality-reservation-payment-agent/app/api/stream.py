# app/api/stream.py
"""
Server-Sent Events endpoints.

This module streams the reservation workflow progress to the client.
For the MVP, the stream emits deterministic workflow milestones and uses
MCP tools for the payment-link step.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncGenerator, Dict

import structlog
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agent_mcp.server import MCPServer
from rag.retriever import retrieve_relevant_policies

logger = structlog.get_logger()

router = APIRouter()


class ReservationStreamRequest(BaseModel):
    """
    Request payload for the streaming reservation flow.
    """

    customer_id: str = Field(..., example="CUST-001")
    room_id: str = Field(..., example="deluxe-suite")
    check_in: str = Field(..., example="2026-08-10")
    check_out: str = Field(..., example="2026-08-12")
    guests: int = Field(default=2, example=2)
    reservation_id: str = Field(default="RES-MVP-001", example="RES-MVP-001")
    idempotency_key: str = Field(
        default="idem_res_mvp_001",
        example="idem_res_mvp_001",
    )


def sse_event(event_name: str, payload: Dict[str, Any]) -> str:
    """
    Build a Server-Sent Events formatted message.
    """
    return (
        f"event: {event_name}\n"
        f"data: {json.dumps(payload)}\n\n"
    )


@router.post("/reserve/stream")
async def reserve_stream(
    request: ReservationStreamRequest,
) -> StreamingResponse:
    """
    Stream the reservation workflow.

    Flow:
        validate_request
        check_availability
        calculate_price
        load_policy_context
        create_payment_link
        pending_payment
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        server = MCPServer()

        try:
            logger.info(
                "reservation_stream_started",
                reservation_id=request.reservation_id,
            )

            yield sse_event(
                "workflow_started",
                {
                    "reservation_id": request.reservation_id,
                    "status": "started",
                },
            )

            await asyncio.sleep(0.5)

            yield sse_event(
                "validate_request",
                {
                    "status": "completed",
                    "message": "Reservation request validated.",
                    "customer_id": request.customer_id,
                    "room_id": request.room_id,
                },
            )

            await asyncio.sleep(0.5)

            availability = server.call_tool(
                "check_availability",
                room_id=request.room_id,
                check_in=request.check_in,
                check_out=request.check_out,
            )

            yield sse_event(
                "check_availability",
                availability,
            )

            if not availability.get("available", False):
                yield sse_event(
                    "workflow_completed",
                    {
                        "status": "ROOM_NOT_AVAILABLE",
                        "reservation_id": request.reservation_id,
                    },
                )
                return

            await asyncio.sleep(0.5)

            pricing = server.call_tool(
                "calculate_price",
                room_id=request.room_id,
                check_in=request.check_in,
                check_out=request.check_out,
                guests=request.guests,
            )

            yield sse_event(
                "calculate_price",
                pricing,
            )

            await asyncio.sleep(0.5)

            policies = retrieve_relevant_policies(
                query="hotel payment cancellation refund policy",
                limit=2,
            )

            yield sse_event(
                "load_policy_context",
                {
                    "status": "completed",
                    "policies_found": len(policies),
                    "policies": policies,
                },
            )

            await asyncio.sleep(0.5)

            payment = server.call_tool(
                "create_payment_link",
                reservation_id=request.reservation_id,
                amount=pricing.get("total_price", 0),
                currency=pricing.get("currency", "USD"),
            )

            yield sse_event(
                "create_payment_link",
                payment,
            )

            await asyncio.sleep(0.5)

            yield sse_event(
                "workflow_completed",
                {
                    "status": "PENDING_PAYMENT",
                    "reservation_id": request.reservation_id,
                    "payment_link": payment.get("payment_link"),
                    "idempotency_key": payment.get(
                        "idempotency_key",
                        request.idempotency_key,
                    ),
                    "safety_rule": (
                        "The agent never charges directly. "
                        "Customer payment happens in Stripe Sandbox."
                    ),
                },
            )

            logger.info(
                "reservation_stream_completed",
                reservation_id=request.reservation_id,
            )

        except Exception as exc:
            logger.error(
                "reservation_stream_failed",
                reservation_id=request.reservation_id,
                error=str(exc),
            )

            yield sse_event(
                "workflow_error",
                {
                    "status": "error",
                    "message": "Reservation workflow failed.",
                },
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )