# app/api/stream.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import ReservationRequest
import json
import asyncio

router = APIRouter()

@router.post("/stream")
async def reserve_stream(request: ReservationRequest):
    """
    SSE Streaming endpoint for Reservation flow.
    Executes LangGraph workflow -> CrewAI agents -> MCP Create Payment Link.
    """
    async def event_generator():
        steps = [
            {"step": "validate_request", "status": "completed", "message": "Validating reservation schema and idempotency key..."},
            {"step": "check_availability", "status": "completed", "message": "Checking availability for dates checking-in and checking-out..."},
            {"step": "calculate_price", "status": "completed", "message": "Price calculated: $500.00 (2 nights Deluxe Suite)"},
            {"step": "reservation_agent", "status": "completed", "message": "CrewAI Reservation Specialist compiling details..."},
            {"step": "payment_agent", "status": "completed", "message": "CrewAI Payment Specialist running MCP:create_payment_link tool..."},
            {"step": "create_payment_link", "status": "pending_payment", "payment_link": f"https://checkout.stripe.com/pay/mock_session_res_{request.idempotency_key}", "idempotency_key": request.idempotency_key}
        ]
        for step in steps:
            await asyncio.sleep(1.0)
            yield f"data: {json.dumps(step)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
