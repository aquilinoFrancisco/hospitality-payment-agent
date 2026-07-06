# integrations/payments/base.py
"""
Payment Provider Contract.

This file defines the common interface that every payment provider must follow.

Why this exists:
    The business workflow should not depend directly on Stripe, Conekta,
    Mercado Pago, or any specific payment vendor.

    PaymentService should only know that there is a provider capable of:
    - creating a payment link;
    - checking payment status;
    - issuing refunds.

    This allows the platform to switch providers without changing LangGraph,
    CrewAI, MCP tools, FastAPI endpoints, or business workflows.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class PaymentProvider(ABC):
    """
    Abstract payment provider.

    All payment integrations must implement this contract.

    Examples:
        - StripeProvider
        - ConektaProvider
        - MercadoPagoProvider
    """

    @abstractmethod
    def create_payment_link(
        self,
        reservation_id: str,
        amount: float,
        currency: str,
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """
        Create a safe payment link.

        The provider returns a checkout/payment URL.

        The agent never charges directly.
        The customer completes the payment through the provider.
        """
        raise NotImplementedError

    @abstractmethod
    def get_payment_status(
        self,
        payment_id: str,
    ) -> Dict[str, Any]:
        """
        Retrieve payment status from the provider.
        """
        raise NotImplementedError

    @abstractmethod
    def refund_payment(
        self,
        payment_id: str,
        amount: float,
        currency: str,
        idempotency_key: str,
    ) -> Dict[str, Any]:
        """
        Issue a refund through the provider.

        Refunds must also be idempotent and auditable.
        """
        raise NotImplementedError