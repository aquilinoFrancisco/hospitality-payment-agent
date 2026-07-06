# crew/reservation_agent.py
"""
Reservation agent definition.

This agent represents the hospitality specialist responsible for validating
guest requirements, reservation intent, room preferences, and booking rules.
"""

import structlog
from crewai import Agent

logger = structlog.get_logger()


def get_reservation_agent() -> Agent:
    """
    Build the CrewAI reservation agent.

    Returns:
        Agent: CrewAI agent focused on reservation validation and booking coordination.
    """
    logger.info("initializing_reservation_agent")

    return Agent(
        role="Hospitality Reservation Specialist",
        goal=(
            "Validate customer requirements, confirm booking intent, "
            "and coordinate room reservation parameters before payment."
        ),
        backstory=(
            "You are an experienced hotel reservations specialist. "
            "You understand room availability, guest requirements, check-in rules, "
            "booking restrictions, and operational compliance. "
            "You never confirm a reservation unless availability and pricing "
            "have already been validated by deterministic MCP tools."
        ),
        verbose=True,
        allow_delegation=False,
    )