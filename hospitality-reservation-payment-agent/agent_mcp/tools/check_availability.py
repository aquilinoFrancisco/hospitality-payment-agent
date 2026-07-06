# agent_mcp/tools/check_availability.py
from services.reservation_service import ReservationService

def check_availability_tool(room_id: str, check_in: str, check_out: str) -> dict:
    """
    MCP Tool: Check availability of a room type for specified dates in the mock database.
    """
    is_available = ReservationService.check_room_availability(room_id, check_in, check_out)
    message = (
        f"Room '{room_id}' is available from {check_in} to {check_out}."
        if is_available
        else f"Room '{room_id}' is NOT available from {check_in} to {check_out}."
    )
    return {
        "available": is_available,
        "room_id": room_id,
        "check_in": check_in,
        "check_out": check_out,
        "message": message
    }

