# agent_mcp/tools/create_payment_link.py
"""
MCP Tool: create_payment_link.

This tool creates a safe payment link for a reservation using a configurable
payment provider.

Supported providers:
- stripe
- conekta
- mercado_pago

Business rule:
The AI agent never charges the customer directly.
The agent only requests a payment link through this controlled tool.
"""

from __future__ import annotations

from typing import Dict

from services.payment_service import PaymentService


def create_payment_link_tool(
    reservation_id: str,
    amount: float,
    currency: str = "usd",
    provider: str = "stripe",
) -> Dict[str, object]:
    """
    Generate a safe payment link.

    Args:
        reservation_id: Reservation identifier.
        amount: Payment amount.
        currency: Payment currency.
        provider: Payment provider. Default is stripe.

    Returns:
        JSON-safe payment link payload.
    """

    idempotency_key = f"idem_pay_{provider}_{reservation_id}"

    result = PaymentService.create_payment_link(
        reservation_id=reservation_id,
        amount=amount,
        currency=currency,
        provider=provider,
        idempotency_key=idempotency_key,
    )

    return {
        "provider": result["provider"],
        "payment_id": result["payment_id"],
        "reservation_id": reservation_id,
        "payment_link": result["payment_link"],
        "payment_session_id": result["payment_session_id"],
        "status": result["status"],
        "amount": result["amount"],
        "currency": result["currency"],
        "idempotency_key": result["idempotency_key"],
        "safety_rule": (
            "Agent creates payment link only. "
            "Payment provider executes payment. "
            "Webhook confirms final payment state."
        ),
    }