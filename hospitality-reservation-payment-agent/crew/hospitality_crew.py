# crew/hospitality_crew.py
import structlog
from crewai import Crew, Process
from crew.reservation_agent import get_reservation_agent
from crew.payment_agent import get_payment_agent
from crew.tasks import get_reservation_task, get_payment_task

logger = structlog.get_logger()

def run_hospitality_crew(inputs: dict):
    logger.info("Running Hospitality Agentic Crew", inputs=inputs)
    res_agent = get_reservation_agent()
    pay_agent = get_payment_agent()

    res_task = get_reservation_task(res_agent)
    pay_task = get_payment_task(pay_agent)

    crew = Crew(
        agents=[res_agent, pay_agent],
        tasks=[res_task, pay_task],
        process=Process.sequential,
        verbose=True
    )
    return "Mock Crew Execution Successful: Payment Link Created"
