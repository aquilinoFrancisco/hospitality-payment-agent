# agent_mcp/tools/issue_refund.py
"""
MCP Tool: issue_refund.

This tool triggers a safe refund through the configured payment provider.

Supported providers:
- stripe
- conekta
- mercado_pago

Business rule:
The AI agent does not refund money directly.
It requests a controlled refund through PaymentService.
"""

from __future__ import annotations

from typing import Dict

from services.payment_service import PaymentService


def issue_refund_tool(
    payment_id: str,
    reason: str,
    provider: str = "stripe",
) -> Dict[str, object]:
    """
    Trigger a safe refund on a previous transaction.
    """

    normalized_provider = provider.lower().strip()
    normalized_payment_id = payment_id.strip()
    normalized_reason = reason.strip()

    payment = PaymentService.get_payment_status(
        payment_id=normalized_payment_id,
        provider=normalized_provider,
    )

    if not payment:
        return {
            "provider": normalized_provider,
            "payment_id": normalized_payment_id,
            "refund_id": None,
            "status": "FAILED",
            "reason": normalized_reason,
            "message": (
                f"Payment record '{normalized_payment_id}' not found."
            ),
        }

    payment_session_id = payment["payment_session_id"]
    amount = payment["amount"]
    currency = payment.get("currency", "usd").lower().strip()
    resolved_provider = payment.get(
        "provider",
        normalized_provider,
    ).lower().strip()

    idempotency_key = (
        f"idem_refund_{resolved_provider}_{normalized_payment_id}"
    )

    result = PaymentService.issue_refund(
        payment_session_id=payment_session_id,
        amount=amount,
        currency=currency,
        provider=resolved_provider,
        idempotency_key=idempotency_key,
    )

    return {
        "provider": result["provider"],
        "payment_id": normalized_payment_id,
        "refund_id": result["refund_id"],
        "status": result["status"],
        "amount_refunded": result["amount_refunded"],
        "currency": result["currency"],
        "idempotency_key": result["idempotency_key"],
        "reason": normalized_reason,
        "message": (
            f"Refund of {amount:.2f} {currency.upper()} processed "
            f"successfully for payment '{normalized_payment_id}' using "
            f"{result['provider']}."
        ),
    }