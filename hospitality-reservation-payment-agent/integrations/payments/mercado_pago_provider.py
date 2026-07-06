# integrations/payments/mercado_pago_provider.py
"""
Mercado Pago Payment Provider.

This file adapts Mercado Pago-style payments to the common PaymentProvider
contract.

Why this exists:

Hospitality businesses in LATAM may prefer Mercado Pago because it is widely
used by customers and supports local payment experiences.

The rest of the system should not know Mercado Pago-specific details.
"""

from __future__ import annotations

from typing import Any, Dict

import structlog

from integrations.payments.base import PaymentProvider

logger = structlog.get_logger()


class MercadoPagoProvider(PaymentProvider):
    """
    Mercado Pago implementation of the PaymentProvider contract.

    Current MVP:
        Mock sandbox behavior only.

    Future:
        Use Mercado Pago Checkout Pro, Checkout API, Webhooks and Refunds.
    """

    def create_payment_link(
        self,
        reservation_id: str,
        amount: float,
        currency: str,
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """
        Create a mock Mercado Pago payment link.
        """

        logger.info(
            "mercado_pago_provider_create_payment_link",
            reservation_id=reservation_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        payment_id = f"mp_preference_{reservation_id}"

        return {
            "provider": "mercado_pago",
            "payment_id": payment_id,
            "payment_link": (
                f"https://sandbox.mercadopago.local/checkout/{payment_id}"
            ),
            "status": "pending_payment",
            "amount": amount,
            "currency": currency,
            "idempotency_key": idempotency_key,
            "supported_methods": [
                "card",
                "spei",
                "oxxo",
                "mercado_pago_wallet",
            ],
            "mode": "mock_sandbox",
        }

    def get_payment_status(
        self,
        payment_id: str,
    ) -> Dict[str, Any]:
        """
        Retrieve mock Mercado Pago payment status.
        """

        logger.info(
            "mercado_pago_provider_get_payment_status",
            payment_id=payment_id,
        )

        return {
            "provider": "mercado_pago",
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
        Create a mock Mercado Pago refund.
        """

        logger.info(
            "mercado_pago_provider_refund_payment",
            payment_id=payment_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        return {
            "provider": "mercado_pago",
            "refund_id": f"mp_refund_{payment_id}",
            "payment_id": payment_id,
            "status": "refunded",
            "amount": amount,
            "currency": currency,
            "idempotency_key": idempotency_key,
            "mode": "mock_sandbox",
        }