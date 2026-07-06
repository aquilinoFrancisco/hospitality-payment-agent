# agent_mcp/tools/issue_refund.py
from services.payment_service import PaymentService

def issue_refund_tool(payment_id: str, reason: str) -> dict:
    """
    MCP Tool: Trigger a safe refund on a previous transaction using PaymentService.
    """
    payment = PaymentService.get_payment_status(payment_id)
    if not payment:
        return {
            "payment_id": payment_id,
            "refund_id": "none",
            "status": "FAILED",
            "reason": reason,
            "message": f"Payment record '{payment_id}' not found."
        }
    
    payment_session_id = payment["payment_session_id"]
    amount = payment["amount"]
    
    res = PaymentService.issue_refund(payment_session_id, amount)
    
    return {
        "payment_id": payment_id,
        "refund_id": f"ref_{payment_id}",
        "status": res["status"],
        "reason": reason,
        "message": f"Refund of ${amount:.2f} processed successfully for payment '{payment_id}'."
    }

