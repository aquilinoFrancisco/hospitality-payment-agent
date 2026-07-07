# app/api/webhooks.py
"""
Payment Provider Webhook endpoints.

This module receives asynchronous notifications from payment providers.

Supported providers:
- stripe
- conekta
- mercado_pago

Business rule:
Webhooks are the only source of truth for payment confirmation.
The AI agent never marks a payment as completed.
"""

from __future__ import annotations

import json
from typing import Any, Dict

import structlog
from fastapi import APIRouter, Header, HTTPException, Path, Request

from services.payment_service import PaymentService

logger = structlog.get_logger()

router = APIRouter()

SUPPORTED_PROVIDERS = {
    "stripe",
    "conekta",
    "mercado_pago",
}


@router.post("/{provider}")
async def payment_webhook(
    provider: str = Path(...),
    request: Request = None,
    provider_signature: str | None = Header(
        default=None,
        alias="Payment-Signature",
    ),
) -> Dict[str, Any]:
    """
    Generic payment webhook.

    MVP behavior:
    - Accepts mock webhook events.
    - Extracts payment_session_id when present.
    - Marks payment as completed through PaymentService.
    - Keeps provider-specific verification as future work.
    """

    provider = provider.lower().strip()

    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=404,
            detail=f"Unsupported provider: {provider}",
        )

    body = await request.body()

    logger.info(
        "payment_webhook_received",
        provider=provider,
        signature_present=provider_signature is not None,
    )

    try:
        event = json.loads(body.decode()) if body else {}

    except Exception as exc:
        logger.warning(
            "payment_webhook_invalid_json_defaulting_mock_event",
            provider=provider,
            error=str(exc),
        )
        event = {}

    event_type = event.get(
        "type",
        "payment.completed",
    )

    data = event.get(
        "data",
        {},
    )

    payment_session_id = (
        data.get("payment_session_id")
        or data.get("session_id")
        or data.get("id")
    )

    logger.info(
        "payment_event_processed",
        provider=provider,
        event_type=event_type,
        payment_session_id=payment_session_id,
    )

    if not payment_session_id:
        return {
            "status": "received",
            "provider": provider,
            "event_type": event_type,
            "message": (
                "Webhook received but no payment_session_id was provided. "
                "No reservation state transition was executed."
            ),
            "source_of_truth": f"{provider} webhook",
        }

    try:
        result = PaymentService.mark_payment_completed(
            payment_session_id=payment_session_id,
        )

    except Exception as exc:
        logger.exception(
            "payment_webhook_state_transition_failed",
            provider=provider,
            payment_session_id=payment_session_id,
        )

        return {
            "status": "FAILED",
            "provider": provider,
            "event_type": event_type,
            "payment_session_id": payment_session_id,
            "error": str(exc),
        }

    return {
        "status": "success",
        "provider": provider,
        "event_type": event_type,
        "payment_session_id": payment_session_id,
        "payment": result,
        "reservation_state": "PAID",
        "next_state": "RESERVATION_CONFIRMED",
        "source_of_truth": f"{provider} webhook",
    }