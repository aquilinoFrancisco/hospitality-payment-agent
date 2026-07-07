# integrations/payments/router.py
"""
Payment Router.

This module connects business payment workflows with the provider-agnostic
payment integration layer.

Purpose:
- Keep PaymentService independent from Stripe, Conekta and Mercado Pago.
- Centralize payment provider selection.
- Normalize provider-specific responses.
- Keep business rules stable while payment providers evolve.

Architecture:

PaymentService
      ↓
PaymentRouter
      ↓
PaymentProviderFactory
      ↓
Stripe / Conekta / Mercado Pago
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import structlog

from core.config import settings
from integrations.payments.factory import PaymentProviderFactory

logger = structlog.get_logger()


class PaymentRouter:
    """
    Routes payment operations through the selected payment provider.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
    ) -> None:
        self.provider_name = (
            provider or settings.PAYMENT_PROVIDER_DEFAULT
        ).lower().strip()

        if self.provider_name not in settings.SUPPORTED_PAYMENT_PROVIDERS:
            raise ValueError(
                f"Unsupported payment provider: {self.provider_name}"
            )

        self.provider = PaymentProviderFactory.create(self.provider_name)

        logger.info(
            "payment_router_initialized",
            provider=self.provider_name,
        )

    def create_payment_link(
        self,
        reservation_id: str,
        amount: float,
        currency: str,
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """
        Create a provider-specific payment link and normalize the response.
        """

        logger.info(
            "payment_router_create_payment_link_called",
            provider=self.provider_name,
            reservation_id=reservation_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        response = self.provider.create_payment_link(
            reservation_id=reservation_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        return {
            "provider": response.get("provider", self.provider_name),
            "payment_id": response.get("payment_id"),
            "payment_link": response.get("payment_link"),
            "payment_session_id": (
                response.get("payment_session_id")
                or response.get("raw_provider_response", {}).get("id")
                or response.get("payment_id")
            ),
            "status": response.get("status", "PENDING"),
            "amount": response.get("amount", amount),
            "currency": response.get("currency", currency),
            "idempotency_key": response.get(
                "idempotency_key",
                idempotency_key,
            ),
            "raw_provider_response": response,
        }

    def get_payment_status(
        self,
        payment_id: str,
    ) -> Dict[str, Any]:
        """
        Retrieve payment status through the selected provider.
        """

        logger.info(
            "payment_router_get_payment_status_called",
            provider=self.provider_name,
            payment_id=payment_id,
        )

        response = self.provider.get_payment_status(payment_id)

        return {
            "provider": response.get("provider", self.provider_name),
            "payment_id": response.get("payment_id", payment_id),
            "status": response.get("status", "unknown"),
            "raw_provider_response": response,
        }

    def refund_payment(
        self,
        payment_id: str,
        amount: float,
        currency: str,
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """
        Issue a refund through the selected provider and normalize the response.
        """

        logger.info(
            "payment_router_refund_payment_called",
            provider=self.provider_name,
            payment_id=payment_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        response = self.provider.refund_payment(
            payment_id=payment_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        return {
            "provider": response.get("provider", self.provider_name),
            "refund_id": response.get("refund_id"),
            "payment_id": response.get("payment_id", payment_id),
            "status": response.get("status", "refunded"),
            "amount": response.get("amount", amount),
            "currency": response.get("currency", currency),
            "idempotency_key": response.get(
                "idempotency_key",
                idempotency_key,
            ),
            "raw_provider_response": response,
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Return payment router health information.
        """

        return {
            "router": "payment_router",
            "provider": self.provider_name,
            "status": "available",
        }