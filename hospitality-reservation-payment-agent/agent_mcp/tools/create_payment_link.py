# agent_mcp/tools/create_payment_link.py
from services.payment_service import PaymentService

def create_payment_link_tool(reservation_id: str, amount: float, currency: str = "usd") -> dict:
    """
    MCP Tool: Generate safe Stripe payment sandbox checkout session url and transition reservation state.
    """
    idempotency_key = f"idem_pay_{reservation_id}"
    res = PaymentService.create_payment_link(reservation_id, amount, idempotency_key)
    
    return {
        "payment_id": res["payment_id"],
        "reservation_id": reservation_id,
        "payment_link": res["payment_link"],
        "status": res["status"],
        "idempotency_key": idempotency_key
    }

