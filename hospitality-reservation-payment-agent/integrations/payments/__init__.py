"""
Payment Integration Package.

This package provides a provider-agnostic payment abstraction for the
Hospitality Reservation Payment Agent.

Current supported providers:

- Stripe Sandbox
- Conekta (Mock)
- Mercado Pago (Mock)

Architecture:

                 LangGraph
                     │
                 MCP Tools
                     │
                     ▼
              PaymentService
                     │
                     ▼
              PaymentRouter
                     │
                     ▼
         PaymentProviderFactory
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
      Stripe     Conekta   MercadoPago

Responsibilities:

PaymentService
    - Business rules
    - Idempotency
    - Reservation state transitions
    - Payment persistence

PaymentRouter
    - Provider selection
    - Response normalization
    - Payment provider routing

PaymentProviderFactory
    - Creates provider implementations

Payment Providers
    - Provider-specific integrations
    - SDK/API communication

Why this package exists:

Business logic never communicates directly with Stripe, Conekta or
Mercado Pago.

Adding a new payment provider should only require implementing the
PaymentProvider contract and registering it in PaymentProviderFactory.
"""

from .base import PaymentProvider
from .router import PaymentRouter
from .factory import PaymentProviderFactory
from .stripe_provider import StripeProvider
from .conekta_provider import ConektaProvider
from .mercado_pago_provider import MercadoPagoProvider

__all__ = [
    "PaymentProvider",
    "PaymentRouter",
    "PaymentProviderFactory",
    "StripeProvider",
    "ConektaProvider",
    "MercadoPagoProvider",
]