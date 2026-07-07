# graph/workflow.py
import sys
import os
import uuid
import datetime
import structlog
from langgraph.graph import StateGraph, END

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.config import settings
from graph.state import ReservationState
from agent_mcp.server import MCPServer

logger = structlog.get_logger()
mcp_server = MCPServer()


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def validate_request(state: ReservationState) -> ReservationState:
    """
    Validate request input and enrich state with country, provider,
    currency and idempotency_key.
    """
    start_time = _now()

    errors = []

    if not state.get("customer_id"):
        errors.append("customer_id is required")
    if not state.get("room_id"):
        errors.append("room_id is required")
    if not state.get("check_in"):
        errors.append("check_in is required")
    if not state.get("check_out"):
        errors.append("check_out is required")
    if not state.get("guests") or state.get("guests") <= 0:
        errors.append("guests must be a positive integer")

    if not errors:
        try:
            date_format = "%Y-%m-%d"
            start_date = datetime.datetime.strptime(state["check_in"], date_format)
            end_date = datetime.datetime.strptime(state["check_out"], date_format)

            if start_date >= end_date:
                errors.append("check_in date must be before check_out date")

        except ValueError:
            errors.append("date format must be YYYY-MM-DD")

    if errors:
        state["error"] = "; ".join(errors)
        state["reservation_state"] = "FAILED"
        state["messages"].append(f"Request validation failed: {state['error']}")

    else:
        country = state.get("country") or settings.DEFAULT_COUNTRY
        provider = state.get("provider") or settings.get_provider_for_country(country)
        currency = state.get("currency") or settings.get_currency_for_country(country)

        state["country"] = country
        state["provider"] = provider
        state["currency"] = currency
        state["idempotency_key"] = state.get("idempotency_key") or (
            f"idem_pay_{provider}_{state.get('reservation_id') or 'pending'}"
        )

        state["reservation_state"] = "VALIDATED"
        state["error"] = None
        state["messages"].append(
            f"Request validated. Provider={provider}, currency={currency}, country={country}."
        )

    logger.info(
        "node_executed",
        node_name="validate_request",
        start_time=start_time,
        end_time=_now(),
        reservation_state=state.get("reservation_state"),
        provider=state.get("provider"),
        currency=state.get("currency"),
        country=state.get("country"),
    )

    return state


def check_availability(state: ReservationState) -> ReservationState:
    """
    Check room availability through MCP.
    """
    start_time = _now()

    if state.get("reservation_state") == "FAILED":
        return state

    result = mcp_server.call_tool(
        "check_availability",
        room_id=state["room_id"],
        check_in=state["check_in"],
        check_out=state["check_out"],
    )

    if result.get("status") == "FAILED":
        state["reservation_state"] = "FAILED"
        state["error"] = result.get("error", "Failed checking availability")
        state["messages"].append(f"Availability check failed: {state['error']}")

    elif result.get("available") is True:
        state["reservation_state"] = "AVAILABILITY_CONFIRMED"
        state["messages"].append(result.get("message", "Room is available."))

    else:
        state["reservation_state"] = "FAILED"
        state["error"] = result.get("message", "Room is not available.")
        state["messages"].append(state["error"])

    logger.info(
        "node_executed",
        node_name="check_availability",
        start_time=start_time,
        end_time=_now(),
        reservation_state=state.get("reservation_state"),
    )

    return state


def calculate_price(state: ReservationState) -> ReservationState:
    """
    Calculate reservation pricing through MCP.
    """
    start_time = _now()

    if state.get("reservation_state") == "FAILED":
        return state

    result = mcp_server.call_tool(
        "calculate_price",
        room_id=state["room_id"],
        check_in=state["check_in"],
        check_out=state["check_out"],
        guests=state["guests"],
    )

    if result.get("status") == "FAILED":
        state["reservation_state"] = "FAILED"
        state["error"] = result.get("error", "Failed to calculate price")
        state["messages"].append(f"Price calculation failed: {state['error']}")

    else:
        state["total_price"] = result.get("total_price")
        state["currency"] = state.get("currency") or result.get("currency", settings.DEFAULT_CURRENCY)
        state["reservation_state"] = "PRICE_CALCULATED"
        state["messages"].append(
            f"Price calculated: {state['currency'].upper()} {state['total_price']}."
        )

    logger.info(
        "node_executed",
        node_name="calculate_price",
        start_time=start_time,
        end_time=_now(),
        reservation_state=state.get("reservation_state"),
        currency=state.get("currency"),
    )

    return state


def create_payment_link(state: ReservationState) -> ReservationState:
    """
    Create a safe payment link through MCP using the selected provider.
    """
    start_time = _now()

    if state.get("reservation_state") == "FAILED":
        return state

    reservation_id = state.get("reservation_id")

    if not reservation_id:
        reservation_id = f"res_{uuid.uuid4().hex[:8]}"
        state["reservation_id"] = reservation_id

    provider = state.get("provider") or settings.PAYMENT_PROVIDER_DEFAULT
    currency = state.get("currency") or settings.DEFAULT_CURRENCY

    state["provider"] = provider
    state["currency"] = currency
    state["idempotency_key"] = state.get("idempotency_key") or (
        f"idem_pay_{provider}_{reservation_id}"
    )

    result = mcp_server.call_tool(
        "create_payment_link",
        reservation_id=reservation_id,
        amount=state["total_price"],
        currency=currency,
        provider=provider,
    )

    if result.get("status") == "FAILED":
        state["reservation_state"] = "FAILED"
        state["error"] = result.get("error", "Failed to create payment link")
        state["messages"].append(f"Payment link generation failed: {state['error']}")

    else:
        state["payment_link"] = result.get("payment_link")
        state["payment_id"] = result.get("payment_id")
        state["payment_session_id"] = result.get("payment_session_id")
        state["payment_state"] = result.get("status", "PENDING")
        state["idempotency_key"] = result.get("idempotency_key", state["idempotency_key"])
        state["reservation_state"] = "PENDING_PAYMENT"

        state["messages"].append(
            f"Payment link generated using {provider}: {state['payment_link']}"
        )

    logger.info(
        "node_executed",
        node_name="create_payment_link",
        start_time=start_time,
        end_time=_now(),
        reservation_state=state.get("reservation_state"),
        provider=state.get("provider"),
        currency=state.get("currency"),
        payment_id=state.get("payment_id"),
        idempotency_key=state.get("idempotency_key"),
    )

    return state


def finish(state: ReservationState) -> ReservationState:
    """
    Complete workflow orchestration.
    """
    start_time = _now()

    state["messages"].append("Orchestration workflow successfully finished.")

    logger.info(
        "node_executed",
        node_name="finish",
        start_time=start_time,
        end_time=_now(),
        reservation_state=state.get("reservation_state"),
        provider=state.get("provider"),
        currency=state.get("currency"),
        country=state.get("country"),
    )

    return state


workflow = StateGraph(ReservationState)

workflow.add_node("validate_request", validate_request)
workflow.add_node("check_availability", check_availability)
workflow.add_node("calculate_price", calculate_price)
workflow.add_node("create_payment_link", create_payment_link)
workflow.add_node("finish", finish)


def route_validation(state: ReservationState) -> str:
    if state.get("reservation_state") == "FAILED":
        return END
    return "check_availability"


def route_availability(state: ReservationState) -> str:
    if state.get("reservation_state") == "FAILED":
        return END
    return "calculate_price"


def route_price(state: ReservationState) -> str:
    if state.get("reservation_state") == "FAILED":
        return END
    return "create_payment_link"


def route_payment_link(state: ReservationState) -> str:
    if state.get("reservation_state") == "FAILED":
        return END
    return "finish"


workflow.set_entry_point("validate_request")

workflow.add_conditional_edges("validate_request", route_validation)
workflow.add_conditional_edges("check_availability", route_availability)
workflow.add_conditional_edges("calculate_price", route_price)
workflow.add_conditional_edges("create_payment_link", route_payment_link)
workflow.add_edge("finish", END)

app_graph = workflow.compile()


if __name__ == "__main__":
    test_state: ReservationState = {
        "reservation_id": None,
        "customer_id": "cust_001",
        "room_id": "deluxe-suite",
        "check_in": "2026-07-10",
        "check_out": "2026-07-15",
        "guests": 2,
        "country": "MX",
        "provider": None,
        "reservation_state": "REQUEST_RECEIVED",
        "payment_state": None,
        "payment_link": None,
        "payment_id": None,
        "payment_session_id": None,
        "idempotency_key": None,
        "total_price": None,
        "currency": None,
        "policy_context": None,
        "messages": [],
        "error": None,
    }

    print("Invoking LangGraph workflow with valid test_state...")

    result = app_graph.invoke(test_state)

    print("\n--- FINAL STATE ---")
    import json
    print(json.dumps(result, indent=2))
    print("-------------------")