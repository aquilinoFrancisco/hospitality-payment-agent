# crew/tasks.py
from crewai import Task

def get_reservation_task(agent) -> Task:
    return Task(
        description="Confirm check-in and check-out dates, verify room availability and matching rate policies.",
        expected_output="A structured validation report confirming availability and calculated rates.",
        agent=agent
    )

def get_payment_task(agent) -> Task:
    return Task(
        description="Prepare a Stripe payment session check link with the verified amount and an idempotency key.",
        expected_output="An active payment checkout URL or sandbox session detail.",
        agent=agent
    )
