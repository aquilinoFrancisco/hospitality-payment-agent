# app/main.py
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.api.stream import router as stream_router
from app.api.webhooks import router as webhook_router

logger = structlog.get_logger()

app = FastAPI(
    title="Hospitality Reservation & Payment AI Agent Platform",
    description="Agentic hotel reservations and safe Stripe Sandbox payments flow",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(stream_router, prefix="/reserve")
app.include_router(webhook_router, prefix="/webhooks")

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...", phase="Phase 1 - Standby Setup")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "phase": "Phase 1 - Placeholder Core Ready"}
