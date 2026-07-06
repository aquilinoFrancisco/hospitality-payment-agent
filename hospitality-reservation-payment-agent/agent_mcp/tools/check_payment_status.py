# agent_mcp/tools/check_payment_status.py
from services.payment_service import PaymentService

def check_payment_status_tool(payment_id: str) -> dict:
    """
    MCP Tool: Query payment status to verify transaction state.
    """
    payment = PaymentService.get_payment_status(payment_id)
    if not payment:
        return {
            "payment_id": payment_id,
            "reservation_id": "unknown",
            "status": "NOT_FOUND"
        }
    return {
        "payment_id": payment["payment_id"],
        "reservation_id": payment["reservation_id"],
        "status": payment["status"]
    }

