# app/api/webhooks.py
"""
Stripe Sandbox Webhook endpoints.

This module receives asynchronous payment notifications.

Current MVP:
    - Mock webhook validation
    - Structured logging
    - Reservation state simulation

Future:
    - Stripe SDK signature verification
    - Reservation persistence
    - Event replay protection
"""

from __future__ import annotations

import json

import structlog
from fastapi import APIRouter, Header, HTTPException, Request

logger = structlog.get_logger()

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(
        default=None,
        alias="Stripe-Signature",
    ),
):
    """
    Stripe webhook endpoint.

    In production this endpoint will:

    1. Verify Stripe signature.
    2. Parse the event.
    3. Update reservation state.
    4. Persist payment information.
    5. Return HTTP 200 immediately.
    """

    body = await request.body()

    logger.info(
        "stripe_webhook_received",
        signature_present=stripe_signature is not None,
    )

    # ---------------------------------------------------------
    # MVP
    # ---------------------------------------------------------

    try:

        event = json.loads(body.decode())

    except Exception:

        event = {
            "type": "checkout.session.completed",
            "data": {},
        }

    event_type = event.get(
        "type",
        "checkout.session.completed",
    )

    logger.info(
        "stripe_event_processed",
        event_type=event_type,
    )

    #
    # Future implementation
    #
    # event = stripe.Webhook.construct_event(
    #     payload=body,
    #     sig_header=stripe_signature,
    #     secret=WEBHOOK_SECRET,
    # )
    #
    # reservation_service.confirm_payment(...)
    #

    return {
        "status": "success",
        "provider": "Stripe Sandbox",
        "event_type": event_type,
        "reservation_state": "PAID",
        "next_state": "RESERVATION_CONFIRMED",
        "source_of_truth": "Stripe Webhook",
    }