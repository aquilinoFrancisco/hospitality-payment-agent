# agent_mcp/tools/create_payment_link.py
"""
MCP Tool: create_payment_link.

This tool creates a safe payment link for a reservation.

Important:
- The AI agent never charges the customer directly.
- This tool only creates a Stripe Sandbox checkout/payment link.
- Stripe webhook confirmation is the source of truth for payment completion.
"""

from __future__ import annotations

from typing import Dict

from services.payment_service import PaymentService


def create_payment_link_tool(
    reservation_id: str,
    amount: float,
    currency: str = "usd",
) -> Dict[str, object]:
    """
    Generate a safe Stripe Sandbox checkout session URL.

    Args:
        reservation_id: Reservation identifier.
        amount: Payment amount.
        currency: Payment currency.

    Returns:
        JSON-safe payment link payload.
    """

    idempotency_key = f"idem_pay_{reservation_id}"

    result = PaymentService.create_payment_link(
        reservation_id=reservation_id,
        amount=amount,
        currency=currency,
        idempotency_key=idempotency_key,
    )

    return {
        "payment_id": result["payment_id"],
        "reservation_id": reservation_id,
        "payment_link": result["payment_link"],
        "status": result["status"],
        "amount": amount,
        "currency": currency,
        "idempotency_key": idempotency_key,
        "safety_rule": (
            "Agent creates payment link only. "
            "Stripe executes payment. "
            "Webhook confirms final payment state."
        ),
    }