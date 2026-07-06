# app/dependencies.py
import structlog

logger = structlog.get_logger()

async def get_db():
    logger.info("Initializing mock database dependency connection")
    yield None

async def get_stripe_client():
    logger.info("Initializing Stripe Sandbox dependency connection")
    yield None
