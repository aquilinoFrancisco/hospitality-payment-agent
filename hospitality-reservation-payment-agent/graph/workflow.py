# graph/workflow.py
import sys
import os
import datetime
import structlog
from langgraph.graph import StateGraph, END

# Align sys.path to resolve relative modules properly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from graph.state import ReservationState
from agent_mcp.server import MCPServer

logger = structlog.get_logger()
mcp_server = MCPServer()

def validate_request(state: ReservationState) -> ReservationState:
    """
    Validates request input fields and date structure.
    """
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
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
        state["reservation_state"] = "VALIDATED"
        state["messages"].append("Request successfully validated.")
        state["error"] = None
        
    end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    logger.info(
        "Node executed",
        node_name="validate_request",
        start_time=start_time,
        end_time=end_time,
        reservation_state=state.get("reservation_state")
    )
    return state

def check_availability(state: ReservationState) -> ReservationState:
    """
    Queries check_availability MCP Tool to verify room type calendar status.
    """
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    if state.get("reservation_state") == "FAILED":
        end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        logger.info(
            "Node executed",
            node_name="check_availability",
            start_time=start_time,
            end_time=end_time,
            reservation_state=state.get("reservation_state")
        )
        return state

    res = mcp_server.call_tool(
        "check_availability",
        room_id=state["room_id"],
        check_in=state["check_in"],
        check_out=state["check_out"]
    )
    
    if res.get("status") == "FAILED":
        state["reservation_state"] = "FAILED"
        state["error"] = res.get("error", "Failed checking availability")
        state["messages"].append(f"Availability check failed: {state['error']}")
    elif res.get("available") is True:
        state["reservation_state"] = "AVAILABILITY_CONFIRMED"
        state["messages"].append(res.get("message", "Room is available."))
    else:
        state["reservation_state"] = "FAILED"
        state["error"] = res.get("message", "Room is not available.")
        state["messages"].append(state["error"])
        
    end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    logger.info(
        "Node executed",
        node_name="check_availability",
        start_time=start_time,
        end_time=end_time,
        reservation_state=state.get("reservation_state")
    )
    return state

def calculate_price(state: ReservationState) -> ReservationState:
    """
    Queries calculate_price MCP Tool to determine stays pricing.
    """
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    if state.get("reservation_state") == "FAILED":
        end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        logger.info(
            "Node executed",
            node_name="calculate_price",
            start_time=start_time,
            end_time=end_time,
            reservation_state=state.get("reservation_state")
        )
        return state

    res = mcp_server.call_tool(
        "calculate_price",
        room_id=state["room_id"],
        check_in=state["check_in"],
        check_out=state["check_out"],
        guests=state["guests"]
    )
    
    if res.get("status") == "FAILED":
        state["reservation_state"] = "FAILED"
        state["error"] = res.get("error", "Failed to calculate price")
        state["messages"].append(f"Price calculation failed: {state['error']}")
    else:
        state["total_price"] = res.get("total_price")
        state["currency"] = res.get("currency", "usd")
        state["reservation_state"] = "PRICE_CALCULATED"
        state["messages"].append(
            f"Price calculated: USD {state['total_price']} for {res.get('nights')} nights."
        )
        
    end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    logger.info(
        "Node executed",
        node_name="calculate_price",
        start_time=start_time,
        end_time=end_time,
        reservation_state=state.get("reservation_state")
    )
    return state

def create_payment_link(state: ReservationState) -> ReservationState:
    """
    Queries create_payment_link MCP Tool to generate a safe Stripe transaction endpoint.
    """
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    if state.get("reservation_state") == "FAILED":
        end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        logger.info(
            "Node executed",
            node_name="create_payment_link",
            start_time=start_time,
            end_time=end_time,
            reservation_state=state.get("reservation_state")
        )
        return state

    reservation_id = state.get("reservation_id")
    if not reservation_id:
        import uuid
        reservation_id = f"res_{uuid.uuid4().hex[:8]}"
        state["reservation_id"] = reservation_id

    res = mcp_server.call_tool(
        "create_payment_link",
        reservation_id=reservation_id,
        amount=state["total_price"],
        currency=state.get("currency") or "usd"
    )
    
    if res.get("status") == "FAILED":
        state["reservation_state"] = "FAILED"
        state["error"] = res.get("error", "Failed to create payment link")
        state["messages"].append(f"Payment link generation failed: {state['error']}")
    else:
        state["payment_link"] = res.get("payment_link")
        state["payment_id"] = res.get("payment_id")
        state["payment_state"] = res.get("status", "PENDING")
        state["reservation_state"] = "PENDING_PAYMENT"
        state["messages"].append(f"Payment link generated: {state['payment_link']}")
        
    end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    logger.info(
        "Node executed",
        node_name="create_payment_link",
        start_time=start_time,
        end_time=end_time,
        reservation_state=state.get("reservation_state")
    )
    return state

def finish(state: ReservationState) -> ReservationState:
    """
    Completes workflow orchestration.
    """
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    state["messages"].append("Orchestration workflow successfully finished.")
    end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    logger.info(
        "Node executed",
        node_name="finish",
        start_time=start_time,
        end_time=end_time,
        reservation_state=state.get("reservation_state")
    )
    return state

# Setup StateGraph
workflow = StateGraph(ReservationState)

# Add Nodes
workflow.add_node("validate_request", validate_request)
workflow.add_node("check_availability", check_availability)
workflow.add_node("calculate_price", calculate_price)
workflow.add_node("create_payment_link", create_payment_link)
workflow.add_node("finish", finish)

# Conditional routing edges
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

# Define Graph Edges
workflow.set_entry_point("validate_request")

workflow.add_conditional_edges("validate_request", route_validation)
workflow.add_conditional_edges("check_availability", route_availability)
workflow.add_conditional_edges("calculate_price", route_price)
workflow.add_conditional_edges("create_payment_link", route_payment_link)
workflow.add_edge("finish", END)

app_graph = workflow.compile()

if __name__ == "__main__":
    # Standard local test simulation
    test_state: ReservationState = {
        "reservation_id": None,
        "customer_id": "cust_001",
        "room_id": "deluxe-suite",
        "check_in": "2026-07-10",
        "check_out": "2026-07-15",
        "guests": 2,
        "reservation_state": "REQUEST_RECEIVED",
        "payment_state": None,
        "payment_link": None,
        "payment_id": None,
        "total_price": None,
        "currency": "usd",
        "messages": [],
        "error": None
    }
    
    print("Invoking LangGraph workflow with valid test_state...")
    result = app_graph.invoke(test_state)
    print("\n--- FINAL STATE ---")
    import json
    print(json.dumps(result, indent=2))
    print("-------------------")
