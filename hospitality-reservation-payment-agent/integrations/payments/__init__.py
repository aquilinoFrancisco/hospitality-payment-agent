"""
Payment Provider Package.

This package contains all payment provider implementations supported by
the Hospitality Reservation Payment Agent.

Current providers:
    - Stripe Sandbox
    - Conekta (Mock)
    - Mercado Pago (Mock)

Architecture:

        PaymentService
              │
              ▼
    PaymentProviderFactory
              │
     ┌────────┼─────────┐
     ▼        ▼         ▼
 Stripe   Conekta   MercadoPago

Why this package exists:

The business layer depends only on the PaymentProvider contract.

Individual payment providers can be added, removed, or replaced without
changing the business workflow.
"""

from .base import PaymentProvider
from .factory import PaymentProviderFactory
from .stripe_provider import StripeProvider
from .conekta_provider import ConektaProvider
from .mercado_pago_provider import MercadoPagoProvider

__all__ = [
    "PaymentProvider",
    "PaymentProviderFactory",
    "StripeProvider",
    "ConektaProvider",
    "MercadoPagoProvider",
]