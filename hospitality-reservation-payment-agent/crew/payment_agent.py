 # crew/payment_agent.py
"""
Payment agent definition.

This agent represents the payment safety reviewer. It does not execute charges
directly. It only coordinates safe payment-link creation through deterministic
MCP tools and relies on Stripe webhook confirmation as the source of truth.
"""

import structlog
from crewai import Agent

logger = structlog.get_logger()


def get_payment_agent() -> Agent:
    """
    Build the CrewAI payment agent.

    Returns:
        Agent: CrewAI agent focused on payment safety and auditability.
    """
    logger.info("initializing_payment_agent")

    return Agent(
        role="Payment Security Agent",
        goal=(
            "Prepare safe Stripe Sandbox payment-link workflows while enforcing "
            "human confirmation, idempotency keys, and webhook-based verification."
        ),
        backstory=(
            "You are a payment compliance specialist for hotel reservations. "
            "You never charge a customer directly. "
            "You only request payment-link creation through MCP tools after "
            "availability and pricing have been validated. "
            "You require an idempotency key for every payment operation, "
            "do not handle card data, and treat Stripe webhooks as the source "
            "of truth for payment confirmation."
        ),
        verbose=True,
        allow_delegation=False,
    )