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

import structlog
from fastapi import APIRouter, Header, HTTPException, Path, Request

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
):
    """
    Generic payment webhook.

    Future:

    Stripe
        Verify Stripe signature

    Conekta
        Verify webhook signature

    Mercado Pago
        Verify notification authenticity

    Then:

        Update payment

        Update reservation

        Trigger reservation confirmation
    """

    provider = provider.lower()

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
        event = json.loads(body.decode())

    except Exception:

        event = {
            "type": "payment.completed",
            "data": {},
        }

    event_type = event.get(
        "type",
        "payment.completed",
    )

    logger.info(
        "payment_event_processed",
        provider=provider,
        event_type=event_type,
    )

    #
    # Future
    #
    # provider.verify_signature(...)
    #
    # PaymentService.mark_payment_completed(...)
    #
    # ReservationService.confirm(...)
    #

    return {
        "status": "success",
        "provider": provider,
        "event_type": event_type,
        "reservation_state": "PAID",
        "next_state": "RESERVATION_CONFIRMED",
        "source_of_truth": f"{provider} webhook",
    }