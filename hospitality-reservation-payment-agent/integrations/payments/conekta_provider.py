# integrations/payments/conekta_provider.py
"""
Conekta Payment Provider.

This file adapts Conekta-style payments to the common PaymentProvider contract.

Why this exists:

Mexico-based hospitality businesses may prefer Conekta because it supports
local payment methods such as cards, SPEI and OXXO.

The rest of the system should not know Conekta-specific details.
"""

from __future__ import annotations

from typing import Any, Dict

import structlog

from integrations.payments.base import PaymentProvider

logger = structlog.get_logger()


class ConektaProvider(PaymentProvider):
    """
    Conekta implementation of the PaymentProvider contract.

    Current MVP:
        Mock sandbox behavior only.

    Future:
        Use Conekta Orders, Charges, Webhooks and Refunds.
    """

    def create_payment_link(
        self,
        reservation_id: str,
        amount: float,
        currency: str,
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """
        Create a mock Conekta payment link.
        """

        logger.info(
            "conekta_provider_create_payment_link",
            reservation_id=reservation_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        payment_id = f"conekta_order_{reservation_id}"

        return {
            "provider": "conekta",
            "payment_id": payment_id,
            "payment_link": (
                f"https://sandbox.conekta.local/pay/{payment_id}"
            ),
            "status": "pending_payment",
            "amount": amount,
            "currency": currency,
            "idempotency_key": idempotency_key,
            "supported_methods": [
                "card",
                "spei",
                "oxxo",
            ],
            "mode": "mock_sandbox",
        }

    def get_payment_status(
        self,
        payment_id: str,
    ) -> Dict[str, Any]:
        """
        Retrieve mock Conekta payment status.
        """

        logger.info(
            "conekta_provider_get_payment_status",
            payment_id=payment_id,
        )

        return {
            "provider": "conekta",
            "payment_id": payment_id,
            "status": "pending_payment",
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
        Create a mock Conekta refund.
        """

        logger.info(
            "conekta_provider_refund_payment",
            payment_id=payment_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        return {
            "provider": "conekta",
            "refund_id": f"conekta_refund_{payment_id}",
            "payment_id": payment_id,
            "status": "refunded",
            "amount": amount,
            "currency": currency,
            "idempotency_key": idempotency_key,
            "mode": "mock_sandbox",
        }