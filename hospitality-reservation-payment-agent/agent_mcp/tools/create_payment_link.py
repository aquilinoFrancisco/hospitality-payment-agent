# agent_mcp/tools/create_payment_link.py
"""
MCP Tool: create_payment_link.

This tool creates a safe payment link for a reservation using a configurable
payment provider.

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
    Generate a safe payment link through PaymentService.

    Architecture:
        MCP Tool
            -> PaymentService
            -> PaymentRouter
            -> PaymentProviderFactory
            -> Payment Provider
    """

    normalized_provider = provider.lower().strip()
    normalized_currency = currency.lower().strip()

    idempotency_key = f"idem_pay_{normalized_provider}_{reservation_id}"

    result = PaymentService.create_payment_link(
        reservation_id=reservation_id,
        amount=amount,
        currency=normalized_currency,
        provider=normalized_provider,
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