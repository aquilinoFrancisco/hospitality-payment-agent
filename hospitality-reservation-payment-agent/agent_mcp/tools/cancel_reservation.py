# agent_mcp/tools/cancel_reservation.py
from services.reservation_service import ReservationService

def cancel_reservation_tool(reservation_id: str, reason: str) -> dict:
    """
    MCP Tool: Cancel a reservation and update state.
    """
    res = ReservationService.cancel_reservation(reservation_id)
    if "error" in res:
        return {
            "reservation_id": reservation_id,
            "reservation_state": "FAILED",
            "cancellation_reason": reason,
            "message": f"Failed to cancel reservation: {res['error']}"
        }
    return {
        "reservation_id": reservation_id,
        "reservation_state": res["reservation_state"],
        "cancellation_reason": reason,
        "message": f"Reservation '{reservation_id}' has been successfully cancelled. Reason: {reason}."
    }

