# crew/payment_agent.py
import structlog
from crewai import Agent

logger = structlog.get_logger()

def get_payment_agent() -> Agent:
    logger.info("Initializing CrewAI Payment Agent")
    return Agent(
        role="Payment Security Agent",
        goal="Generate Stripe payment links securely, applying strict verification and idempotency keys.",
        backstory="A certified financial compliance agent with expertise in digital checkouts and Stripe sandbox operations.",
        verbose=True,
        allow_delegation=False
    )
