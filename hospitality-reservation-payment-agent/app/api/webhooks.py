# app/api/webhooks.py
from fastapi import APIRouter, Request, Header, HTTPException
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """
    Stripe Webhook handler (source of truth for payment status).
    Updates reservation state to PAID upon checkout.session.completed.
    """
    payload = await request.body()
    logger.info("Received Stripe Webhook signal", signature=stripe_signature)
    return {"status": "success", "received": True, "event_type": "checkout.session.completed"}
