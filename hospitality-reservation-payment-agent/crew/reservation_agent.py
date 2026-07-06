# crew/reservation_agent.py
import structlog
from crewai import Agent

logger = structlog.get_logger()

def get_reservation_agent() -> Agent:
    logger.info("Initializing CrewAI Reservation Agent")
    return Agent(
        role="Hospitality Specialist",
        goal="Validate customer requirements and coordinate room booking parameters.",
        backstory="An expert hotel front-desk and reservations manager specializing in details and compliance.",
        verbose=True,
        allow_delegation=False
    )
