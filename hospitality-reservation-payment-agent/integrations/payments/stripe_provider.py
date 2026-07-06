# integrations/payments/stripe_provider.py
"""
Stripe Payment Provider.

This file adapts Stripe Sandbox behavior to the common PaymentProvider contract.

Why this exists:

The rest of the system should not know Stripe-specific details.

PaymentService calls a generic PaymentProvider.
StripeProvider translates that generic contract into Stripe-style behavior.

This keeps LangGraph, CrewAI, MCP tools and FastAPI independent from Stripe.
"""

from __future__ import annotations

from typing import Any, Dict

import structlog

from integrations.payments.base import PaymentProvider
from integrations.stripe.client import StripeSandboxClient

logger = structlog.get_logger()


class StripeProvider(PaymentProvider):
    """
    Stripe implementation of the PaymentProvider contract.

    Current MVP:
        Uses StripeSandboxClient in mock mode.

    Future:
        Uses real Stripe SDK Checkout Sessions, Refunds and Webhooks.
    """

    def __init__(self) -> None:
        self.client = StripeSandboxClient()

    def create_payment_link(
        self,
        reservation_id: str,
        amount: float,
        currency: str,
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """
        Create a Stripe Sandbox checkout session.
        """

        logger.info(
            "stripe_provider_create_payment_link",
            reservation_id=reservation_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        session = self.client.create_checkout_session(
            reservation_id=reservation_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        return {
            "provider": "stripe",
            "payment_id": session["id"],
            "payment_link": session["url"],
            "status": session["payment_status"],
            "amount": amount,
            "currency": currency,
            "idempotency_key": idempotency_key,
            "raw_provider_response": session,
        }

    def get_payment_status(
        self,
        payment_id: str,
    ) -> Dict[str, Any]:
        """
        Retrieve Stripe payment status.

        MVP:
            Returns a mock unpaid status.
        """

        logger.info(
            "stripe_provider_get_payment_status",
            payment_id=payment_id,
        )

        return {
            "provider": "stripe",
            "payment_id": payment_id,
            "status": "unpaid",
            "mode": "mock_sandbox",
        }

    def refund_payment(
        self,
        payment_id: str,
        amount: float,
        currency: str,
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """
        Create a Stripe refund.
        """

        logger.info(
            "stripe_provider_refund_payment",
            payment_id=payment_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        refund = self.client.refund_payment(
            charge_id=payment_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        return {
            "provider": "stripe",
            "refund_id": refund["id"],
            "payment_id": payment_id,
            "status": refund["status"],
            "amount": amount,
            "currency": currency,
            "idempotency_key": idempotency_key,
            "raw_provider_response": refund,
        }