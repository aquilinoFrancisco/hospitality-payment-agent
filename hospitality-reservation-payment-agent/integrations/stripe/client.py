# integrations/stripe/client.py
"""
Stripe Sandbox client wrapper.

Current MVP:
    - Mock Stripe Checkout Session
    - Mock Refund
    - No real credentials required
    - No Stripe SDK required

Future production:
    - Enable Stripe SDK
    - Verify webhooks
    - Use real Checkout Sessions
    - Use idempotency keys on every payment operation
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger()


class StripeSandboxClient:
    """
    Stripe Sandbox client wrapper.

    This class isolates Stripe-specific logic from the rest of the platform.
    MCP tools and services should not depend directly on the Stripe SDK.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("STRIPE_SECRET_KEY")
        self.sandbox_mode = True

        logger.info(
            "stripe_sandbox_client_initialized",
            has_api_key=bool(self.api_key),
            sandbox_mode=self.sandbox_mode,
        )

    def create_checkout_session(
        self,
        reservation_id: str,
        amount: float,
        idempotency_key: str,
        currency: str = "usd",
        success_url: str = "https://example.com/payment-success",
        cancel_url: str = "https://example.com/payment-cancelled",
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout Session.

        Current MVP:
            Returns a mock Checkout Session.

        Future production:
            Use stripe.checkout.Session.create(...)

        Important:
            The AI agent never charges directly.
            It only creates a payment link.
            Stripe executes the payment.
            Webhooks confirm the result.
        """

        logger.info(
            "stripe_mock_create_checkout_session",
            reservation_id=reservation_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        amount_cents = int(amount * 100)

        # -----------------------------------------------------
        # Future real Stripe SDK implementation
        # -----------------------------------------------------
        #
        # import stripe
        #
        # stripe.api_key = self.api_key
        #
        # session = stripe.checkout.Session.create(
        #     mode="payment",
        #     success_url=success_url,
        #     cancel_url=cancel_url,
        #     line_items=[
        #         {
        #             "price_data": {
        #                 "currency": currency,
        #                 "product_data": {
        #                     "name": f"Hotel reservation {reservation_id}",
        #                 },
        #                 "unit_amount": amount_cents,
        #             },
        #             "quantity": 1,
        #         }
        #     ],
        #     metadata={
        #         "reservation_id": reservation_id,
        #         "idempotency_key": idempotency_key,
        #     },
        #     idempotency_key=idempotency_key,
        # )
        #
        # return {
        #     "id": session.id,
        #     "url": session.url,
        #     "amount_total": session.amount_total,
        #     "currency": session.currency,
        #     "payment_status": session.payment_status,
        #     "metadata": session.metadata,
        # }

        return {
            "id": f"cs_test_mock_{idempotency_key[:8]}",
            "url": f"https://checkout.stripe.com/pay/mock_session_{reservation_id}",
            "amount_total": amount_cents,
            "currency": currency,
            "payment_status": "unpaid",
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {
                "reservation_id": reservation_id,
                "idempotency_key": idempotency_key,
            },
            "mode": "mock_sandbox",
        }

    def refund_payment(
        self,
        charge_id: str,
        amount: float,
        idempotency_key: str,
        currency: str = "usd",
    ) -> Dict[str, Any]:
        """
        Create a refund.

        Current MVP:
            Returns a mock refund response.

        Future production:
            Use stripe.Refund.create(...)
        """

        logger.info(
            "stripe_mock_refund_payment",
            charge_id=charge_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        amount_cents = int(amount * 100)

        # -----------------------------------------------------
        # Future real Stripe SDK implementation
        # -----------------------------------------------------
        #
        # import stripe
        #
        # stripe.api_key = self.api_key
        #
        # refund = stripe.Refund.create(
        #     charge=charge_id,
        #     amount=amount_cents,
        #     metadata={
        #         "idempotency_key": idempotency_key,
        #     },
        #     idempotency_key=idempotency_key,
        # )
        #
        # return {
        #     "id": refund.id,
        #     "amount": refund.amount,
        #     "currency": refund.currency,
        #     "status": refund.status,
        #     "charge": refund.charge,
        # }

        return {
            "id": f"re_test_mock_{idempotency_key[:8]}",
            "amount": amount_cents,
            "currency": currency,
            "status": "succeeded",
            "charge": charge_id,
            "metadata": {
                "idempotency_key": idempotency_key,
            },
            "mode": "mock_sandbox",
        }