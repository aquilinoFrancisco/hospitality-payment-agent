# crew/hospitality_crew.py
"""
Hospitality Crew orchestration.

This module wires the ReservationAgent and PaymentAgent into a sequential
CrewAI workflow. For the MVP, it returns a JSON-safe execution summary that
can be consumed later by LangGraph and FastAPI.
"""

from typing import Any, Dict

import structlog
from crewai import Crew, Process

from crew.payment_agent import get_payment_agent
from crew.reservation_agent import get_reservation_agent
from crew.tasks import (
    get_confirmation_task,
    get_payment_task,
    get_reservation_task,
)

logger = structlog.get_logger()


def run_hospitality_crew(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the hospitality multi-agent workflow.

    Args:
        inputs: Reservation and payment context.

    Returns:
        JSON-safe dictionary with crew execution metadata.
    """
    logger.info("running_hospitality_crew", inputs=inputs)

    reservation_agent = get_reservation_agent()
    payment_agent = get_payment_agent()

    reservation_task = get_reservation_task(reservation_agent)
    payment_task = get_payment_task(payment_agent)
    confirmation_task = get_confirmation_task(payment_agent)

    crew = Crew(
        agents=[reservation_agent, payment_agent],
        tasks=[reservation_task, payment_task, confirmation_task],
        process=Process.sequential,
        verbose=True,
    )

    # MVP safety:
    # We build the CrewAI workflow but avoid relying on real LLM execution here.
    # The production version can call crew.kickoff(inputs=inputs) when credentials
    # and runtime configuration are available.
    return {
        "status": "CREW_CONFIGURED",
        "mode": "MVP_SAFE_NO_LLM_EXECUTION",
        "reservation_id": inputs.get("reservation_id"),
        "customer_id": inputs.get("customer_id"),
        "room_id": inputs.get("room_id"),
        "agents": [
            "ReservationAgent",
            "PaymentAgent",
        ],
        "tasks": [
            "validate_reservation",
            "prepare_payment_link",
            "confirm_reservation_after_webhook",
        ],
        "payment_safety_rule": (
            "The agent never charges directly. It only prepares a payment link; "
            "Stripe webhook confirmation is the source of truth."
        ),
        "next_state": "PENDING_PAYMENT",
    }