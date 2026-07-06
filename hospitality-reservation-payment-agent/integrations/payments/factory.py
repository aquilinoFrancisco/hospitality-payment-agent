# integrations/payments/factory.py

"""
Payment Provider Factory.

Why this exists:

The business layer should never instantiate a specific payment provider.

Instead, it asks this factory for the configured provider.

Benefits:

- Easy provider replacement.
- No business logic changes.
- Cleaner dependency management.
- Better testing with mock providers.
"""

from __future__ import annotations

from integrations.payments.base import PaymentProvider
from integrations.payments.stripe_provider import StripeProvider
from integrations.payments.conekta_provider import ConektaProvider
from integrations.payments.mercado_pago_provider import MercadoPagoProvider


class PaymentProviderFactory:
    """
    Creates payment provider implementations.

    Current default:
        Stripe Sandbox

    Future:
        Read provider from configuration or environment variables.
    """

    @staticmethod
    def create(provider: str = "stripe") -> PaymentProvider:
        """
        Return the configured payment provider.

        Supported providers:

        - stripe
        - conekta
        - mercado_pago
        """

        provider = provider.lower().strip()

        if provider == "stripe":
            return StripeProvider()

        if provider == "conekta":
            return ConektaProvider()

        if provider == "mercado_pago":
            return MercadoPagoProvider()

        raise ValueError(
            f"Unsupported payment provider: {provider}"
        )