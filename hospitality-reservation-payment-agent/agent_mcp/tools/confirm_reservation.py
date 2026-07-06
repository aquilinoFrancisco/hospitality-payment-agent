# agent_mcp/tools/confirm_reservation.py
from services.reservation_service import ReservationService

def confirm_reservation_tool(reservation_id: str) -> dict:
    """
    MCP Tool: Confirm and commit an active reservation booking.
    """
    res = ReservationService.confirm_reservation(reservation_id)
    if "error" in res:
        return {
            "reservation_id": reservation_id,
            "reservation_state": "FAILED",
            "message": f"Failed to confirm reservation: {res['error']}"
        }
    return {
        "reservation_id": reservation_id,
        "reservation_state": res["reservation_state"],
        "message": f"Reservation '{reservation_id}' has been successfully confirmed."
    }

