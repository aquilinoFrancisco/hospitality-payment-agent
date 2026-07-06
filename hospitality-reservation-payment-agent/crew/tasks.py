# crew/tasks.py
"""
CrewAI task definitions for the Hospitality Reservation Payment Agent.

Each task represents a business capability executed by a specialized agent.
Tasks orchestrate business activities but do not implement business logic.
"""

from crewai import Task


def get_reservation_task(agent) -> Task:
    """
    Reservation validation task.

    Validates booking details before any payment operation.
    """
    return Task(
        description=(
            "Validate the reservation request, verify check-in and check-out "
            "dates, confirm room availability, and ensure pricing policies "
            "have been correctly applied."
        ),
        expected_output=(
            "A structured reservation validation report including room "
            "availability, calculated total price, and booking status."
        ),
        agent=agent,
    )


def get_payment_task(agent) -> Task:
    """
    Payment preparation task.

    Creates a secure payment session after reservation validation.
    """
    return Task(
        description=(
            "Prepare a Stripe Sandbox payment link using the validated "
            "reservation amount. Generate an idempotency key and ensure "
            "payment safety rules are respected."
        ),
        expected_output=(
            "A payment session containing payment_id, payment_link, "
            "reservation_id and idempotency_key."
        ),
        agent=agent,
    )


def get_confirmation_task(agent) -> Task:
    """
    Reservation confirmation task.

    Confirms the reservation only after successful payment verification.
    """
    return Task(
        description=(
            "Confirm the reservation only after payment has been verified "
            "through the Stripe webhook event."
        ),
        expected_output=(
            "Reservation confirmation with reservation_state="
            "RESERVATION_CONFIRMED."
        ),
        agent=agent,
    )