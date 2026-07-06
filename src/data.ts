// src/data.ts

export interface RepoFile {
  path: string;
  name: string;
  language: 'python' | 'markdown' | 'json' | 'toml' | 'dockerfile' | 'yaml' | 'ini';
  description: string;
  content: string;
}

export interface FolderNode {
  name: string;
  path: string;
  type: 'folder' | 'file';
  children?: FolderNode[];
}

export const REPO_FILES: Record<string, RepoFile> = {
  'app/main.py': {
    path: 'app/main.py',
    name: 'main.py',
    language: 'python',
    description: 'The central gateway API router for FastAPI, managing Middlewares, REST controllers, Webhook, and SSE subscriptions.',
    content: `# app/main.py
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.api.stream import router as stream_router
from app.api.webhooks import router as webhook_router

logger = structlog.get_logger()

app = FastAPI(
    title="Hospitality Reservation & Payment AI Agent Platform",
    description="Agentic hotel reservations and safe Stripe Sandbox payments flow",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(stream_router, prefix="/reserve")
app.include_router(webhook_router, prefix="/webhooks")

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...", phase="Phase 1 - Standby Setup")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "phase": "Phase 1 - Placeholder Core Ready"}`
  },
  'app/dependencies.py': {
    path: 'app/dependencies.py',
    name: 'dependencies.py',
    language: 'python',
    description: 'Defines dependency injection providers for FastAPI, including database sessions and Stripe Sandbox SDK hooks.',
    content: `# app/dependencies.py
import structlog

logger = structlog.get_logger()

async def get_db():
    logger.info("Initializing mock database dependency connection")
    yield None

async def get_stripe_client():
    logger.info("Initializing Stripe Sandbox dependency connection")
    yield None`
  },
  'app/api/routes.py': {
    path: 'app/api/routes.py',
    name: 'routes.py',
    language: 'python',
    description: 'REST routes for rooms listings and detailed reservation queries.',
    content: `# app/api/routes.py
from fastapi import APIRouter, Depends
from models.schemas import ReservationResponse

router = APIRouter()

@router.get("/rooms")
async def list_rooms():
    """Get all available rooms from mock data"""
    return [
        {"id": "deluxe-suite", "name": "Deluxe Suite", "base_price": 250.00, "capacity": 3},
        {"id": "standard-queen", "name": "Standard Queen Room", "base_price": 140.00, "capacity": 2},
        {"id": "penthouse", "name": "Panoramic Penthouse", "base_price": 600.00, "capacity": 5}
    ]

@router.get("/reservations/{reservation_id}")
async def get_reservation(reservation_id: str):
    """Get reservation detail and status"""
    return {
        "reservation_id": reservation_id,
        "customer_email": "aquilino.francisco@gmail.com",
        "room_type": "deluxe-suite",
        "status": "PENDING_PAYMENT",
        "payment_link": f"https://checkout.stripe.com/pay/mock_session_{reservation_id}",
        "total_price": 500.00,
        "idempotency_key": "idem_key_abc123"
    }`
  },
  'app/api/stream.py': {
    path: 'app/api/stream.py',
    name: 'stream.py',
    language: 'python',
    description: 'Server-Sent Events streaming handler. Streams real-time reservation progress and final payment checkout urls.',
    content: `# app/api/stream.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import ReservationRequest
import json
import asyncio

router = APIRouter()

@router.post("/stream")
async def reserve_stream(request: ReservationRequest):
    """
    SSE Streaming endpoint for Reservation flow.
    Executes LangGraph workflow -> CrewAI agents -> MCP Create Payment Link.
    """
    async def event_generator():
        steps = [
            {"step": "validate_request", "status": "completed", "message": "Validating reservation schema and idempotency key..."},
            {"step": "check_availability", "status": "completed", "message": "Checking availability for dates checking-in and checking-out..."},
            {"step": "calculate_price", "status": "completed", "message": "Price calculated: $500.00 (2 nights Deluxe Suite)"},
            {"step": "reservation_agent", "status": "completed", "message": "CrewAI Reservation Specialist compiling details..."},
            {"step": "payment_agent", "status": "completed", "message": "CrewAI Payment Specialist running MCP:create_payment_link tool..."},
            {"step": "create_payment_link", "status": "pending_payment", "payment_link": f"https://checkout.stripe.com/pay/mock_session_res_{request.idempotency_key}", "idempotency_key": request.idempotency_key}
        ]
        for step in steps:
            await asyncio.sleep(1.0)
            yield f"data: {json.dumps(step)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")`
  },
  'app/api/webhooks.py': {
    path: 'app/api/webhooks.py',
    name: 'webhooks.py',
    language: 'python',
    description: 'Receives cryptographically verified events from Stripe, acting as the absolute authority for transitions to PAID.',
    content: `# app/api/webhooks.py
from fastapi import APIRouter, Request, Header, HTTPException
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """
    Stripe Webhook handler (source of truth for payment status).
    Updates reservation state to PAID upon checkout.session.completed.
    """
    payload = await request.body()
    logger.info("Received Stripe Webhook signal", signature=stripe_signature)
    return {"status": "success", "received": True, "event_type": "checkout.session.completed"}`
  },
  'graph/state.py': {
    path: 'graph/state.py',
    name: 'state.py',
    language: 'python',
    description: 'Pydantic/TypedDict state definitions representing the thread context passed between LangGraph nodes.',
    content: `# graph/state.py
from typing import TypedDict, List, Optional

class ReservationState(TypedDict):
    reservation_id: Optional[str]
    customer_id: Optional[str]
    room_id: Optional[str]
    check_in: Optional[str]
    check_out: Optional[str]
    guests: Optional[int]
    reservation_state: Optional[str]
    payment_state: Optional[str]
    payment_link: Optional[str]
    payment_id: Optional[str]
    total_price: Optional[float]
    currency: Optional[str]
    messages: List[str]
    error: Optional[str]`
  },
  'graph/workflow.py': {
    path: 'graph/workflow.py',
    name: 'workflow.py',
    language: 'python',
    description: 'The compiled LangGraph routing workflow connecting state evaluation, validation, and CrewAI orchestration.',
    content: `# graph/workflow.py
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

app_graph = workflow.compile()`
  },
  'crew/reservation_agent.py': {
    path: 'crew/reservation_agent.py',
    name: 'reservation_agent.py',
    language: 'python',
    description: 'CrewAI agent designed to represent a hotel hospitality specialist, validating parameters.',
    content: `# crew/reservation_agent.py
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
    )`
  },
  'crew/payment_agent.py': {
    path: 'crew/payment_agent.py',
    name: 'payment_agent.py',
    language: 'python',
    description: 'CrewAI agent designed to represent a payment security compliance officer, safely producing Stripe Sandbox checkout links.',
    content: `# crew/payment_agent.py
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
    )`
  },
  'crew/tasks.py': {
    path: 'crew/tasks.py',
    name: 'tasks.py',
    language: 'python',
    description: 'Defines the descriptive tasks to be sequentially completed by CrewAI agents.',
    content: `# crew/tasks.py
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
    )`
  },
  'crew/hospitality_crew.py': {
    path: 'crew/hospitality_crew.py',
    name: 'hospitality_crew.py',
    language: 'python',
    description: 'Coordinates agents and tasks in a sequential process representing the Core reservation squad.',
    content: `# crew/hospitality_crew.py
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
    return "Mock Crew Execution Successful: Payment Link Created"`
  },
  'agent_mcp/server.py': {
    path: 'agent_mcp/server.py',
    name: 'server.py',
    language: 'python',
    description: 'Hosts the Model Context Protocol (MCP) server, exposing decoupled business actions as structured tools.',
    content: `# agent_mcp/server.py
import structlog
from typing import Dict, Any, List
from agent_mcp.tools import (
    check_availability_tool,
    calculate_price_tool,
    create_payment_link_tool,
    check_payment_status_tool,
    confirm_reservation_tool,
    cancel_reservation_tool,
    issue_refund_tool,
    save_reservation_report_tool
)

logger = structlog.get_logger()

class MCPServer:
    """
    Simple Model Context Protocol (MCP) Server Registry routing LLM agent tool-calls.
    Exposes and coordinates execution of business service tools.
    """
    def __init__(self):
        self._registry = {
            "check_availability": check_availability_tool,
            "calculate_price": calculate_price_tool,
            "create_payment_link": create_payment_link_tool,
            "check_payment_status": check_payment_status_tool,
            "confirm_reservation": confirm_reservation_tool,
            "cancel_reservation": cancel_reservation_tool,
            "issue_refund": issue_refund_tool,
            "save_reservation_report": save_reservation_report_tool
        }
        logger.info("MCP Server registry initialized", registered_tools=list(self._registry.keys()))

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        Lists metadata for all registered MCP tools.
        """
        return [
            {
                "name": "check_availability",
                "description": "Checks the mock database for room type availability within date bounds.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "room_id": {"type": "string"},
                        "check_in": {"type": "string"},
                        "check_out": {"type": "string"}
                    },
                    "required": ["room_id", "check_in", "check_out"]
                }
            },
            {
                "name": "calculate_price",
                "description": "Calculates detailed price breakdown (nights, price per night, total price) for a room.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "room_id": {"type": "string"},
                        "check_in": {"type": "string"},
                        "check_out": {"type": "string"},
                        "guests": {"type": "integer"}
                    },
                    "required": ["room_id", "check_in", "check_out", "guests"]
                }
            },
            {
                "name": "create_payment_link",
                "description": "Generate a fake Stripe Sandbox checkout session payment link.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "reservation_id": {"type": "string"},
                        "amount": {"type": "number"},
                        "currency": {"type": "string"}
                    },
                    "required": ["reservation_id", "amount"]
                }
            },
            {
                "name": "check_payment_status",
                "description": "Checks transaction status for a specific payment ID.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "payment_id": {"type": "string"}
                    },
                    "required": ["payment_id"]
                }
            },
            {
                "name": "confirm_reservation",
                "description": "Confirms and activates a reservation.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "reservation_id": {"type": "string"}
                    },
                    "required": ["reservation_id"]
                }
            },
            {
                "name": "cancel_reservation",
                "description": "Cancels a reservation and releases the blocked calendar room.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "reservation_id": {"type": "string"},
                        "reason": {"type": "string"}
                    },
                    "required": ["reservation_id", "reason"]
                }
            },
            {
                "name": "issue_refund",
                "description": "Issues a mock refund for a completed payment.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "payment_id": {"type": "string"},
                        "reason": {"type": "string"}
                    },
                    "required": ["payment_id", "reason"]
                }
            },
            {
                "name": "save_reservation_report",
                "description": "Saves a structural receipt JSON report for a reservation.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "report_payload": {"type": "object"}
                    },
                    "required": ["report_payload"]
                }
            }
        ]

    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Executes a tool by its registered name with provided arguments.
        """
        logger.info("MCP call_tool triggered", tool_name=tool_name, arguments=kwargs)
        tool_func = self._registry.get(tool_name)
        if not tool_func:
            error_msg = f"Tool '{tool_name}' is not registered."
            logger.error("MCP tool execution failed: Unknown tool", tool_name=tool_name)
            return {"error": error_msg, "status": "FAILED"}
        
        try:
            result = tool_func(**kwargs)
            logger.info("MCP tool execution successful", tool_name=tool_name)
            return result
        except Exception as e:
            error_msg = f"Failed to execute tool '{tool_name}': {str(e)}"
            logger.exception("MCP tool execution exception occurred", tool_name=tool_name)
            return {"error": error_msg, "status": "FAILED"}`
  },
  'agent_mcp/tools/check_availability.py': {
    path: 'agent_mcp/tools/check_availability.py',
    name: 'check_availability.py',
    language: 'python',
    description: 'MCP Tool: Verifies mock availability calendars prior to booking confirmations.',
    content: `# agent_mcp/tools/check_availability.py
from services.reservation_service import ReservationService

def check_availability_tool(room_id: str, check_in: str, check_out: str) -> dict:
    """
    MCP Tool: Check availability of a room type for specified dates in the mock database.
    """
    is_available = ReservationService.check_room_availability(room_id, check_in, check_out)
    message = (
        f"Room '{room_id}' is available from {check_in} to {check_out}."
        if is_available
        else f"Room '{room_id}' is NOT available from {check_in} to {check_out}."
    )
    return {
        "available": is_available,
        "room_id": room_id,
        "check_in": check_in,
        "check_out": check_out,
        "message": message
    }`
  },
  'agent_mcp/tools/calculate_price.py': {
    path: 'agent_mcp/tools/calculate_price.py',
    name: 'calculate_price.py',
    language: 'python',
    description: 'MCP Tool: Computes daily pricing tiers and totals given booking duration.',
    content: `# agent_mcp/tools/calculate_price.py
from datetime import datetime
from services.payment_service import PaymentService

def calculate_price_tool(room_id: str, check_in: str, check_out: str, guests: int) -> dict:
    """
    MCP Tool: Calculate reservation pricing breakdown based on room type, dates, and number of guests.
    """
    total_price = PaymentService.calculate_price(room_id, check_in, check_out)
    
    try:
        date_format = "%Y-%m-%d"
        start_date = datetime.strptime(check_in, date_format)
        end_date = datetime.strptime(check_out, date_format)
        delta = end_date - start_date
        nights = max(1, delta.days)
    except Exception:
        nights = 1

    price_per_night = round(total_price / nights, 2)

    return {
        "room_id": room_id,
        "nights": nights,
        "price_per_night": price_per_night,
        "total_price": total_price,
        "currency": "usd"
    }`
  },
  'agent_mcp/tools/create_payment_link.py': {
    path: 'agent_mcp/tools/create_payment_link.py',
    name: 'create_payment_link.py',
    language: 'python',
    description: 'MCP Tool: Interfaces with Stripe SDK to request checkout session link generations using idempotency codes.',
    content: `# agent_mcp/tools/create_payment_link.py
from services.payment_service import PaymentService

def create_payment_link_tool(reservation_id: str, amount: float, currency: str = "usd") -> dict:
    """
    MCP Tool: Generate safe Stripe payment sandbox checkout session url and transition reservation state.
    """
    idempotency_key = f"idem_pay_{reservation_id}"
    res = PaymentService.create_payment_link(reservation_id, amount, idempotency_key)
    
    return {
        "payment_id": res["payment_id"],
        "reservation_id": reservation_id,
        "payment_link": res["payment_link"],
        "status": res["status"],
        "idempotency_key": idempotency_key
    }`
  },
  'agent_mcp/tools/check_payment_status.py': {
    path: 'agent_mcp/tools/check_payment_status.py',
    name: 'check_payment_status.py',
    language: 'python',
    description: 'MCP Tool: Verifies payment states from the checkout session tracking ID.',
    content: `# agent_mcp/tools/check_payment_status.py
from services.payment_service import PaymentService

def check_payment_status_tool(payment_id: str) -> dict:
    """
    MCP Tool: Query payment status to verify transaction state.
    """
    payment = PaymentService.get_payment_status(payment_id)
    if not payment:
        return {
            "payment_id": payment_id,
            "reservation_id": "unknown",
            "status": "NOT_FOUND"
        }
    return {
        "payment_id": payment["payment_id"],
        "reservation_id": payment["reservation_id"],
        "status": payment["status"]
    }`
  },
  'agent_mcp/tools/confirm_reservation.py': {
    path: 'agent_mcp/tools/confirm_reservation.py',
    name: 'confirm_reservation.py',
    language: 'python',
    description: 'MCP Tool: Moves reservation records from PENDING_PAYMENT to CONFIRMED on verified payments.',
    content: `# agent_mcp/tools/confirm_reservation.py
from services.reservation_service import ReservationService

def confirm_reservation_tool(reservation_id: str) -> dict:
    """
    MCP Tool: Confirm and commit an active reservation booking.
    """
    res = ReservationService.confirm_reservation(reservation_id)
    if "error" in res:
        return {
            "reservation_id": reservation_id,
            "reservation_state": "FAILED",
            "message": f"Failed to confirm reservation: {res['error']}"
        }
    return {
        "reservation_id": reservation_id,
        "reservation_state": res["reservation_state"],
        "message": f"Reservation '{reservation_id}' has been successfully confirmed."
    }`
  },
  'agent_mcp/tools/cancel_reservation.py': {
    path: 'agent_mcp/tools/cancel_reservation.py',
    name: 'cancel_reservation.py',
    language: 'python',
    description: 'MCP Tool: Safely handles cancellation logic and calendar releases.',
    content: `# agent_mcp/tools/cancel_reservation.py
from services.reservation_service import ReservationService

def cancel_reservation_tool(reservation_id: str, reason: str) -> dict:
    """
    MCP Tool: Cancel a reservation and update state.
    """
    res = ReservationService.cancel_reservation(reservation_id)
    if "error" in res:
        return {
            "reservation_id": reservation_id,
            "reservation_state": "FAILED",
            "cancellation_reason": reason,
            "message": f"Failed to cancel reservation: {res['error']}"
        }
    return {
        "reservation_id": reservation_id,
        "reservation_state": res["reservation_state"],
        "cancellation_reason": reason,
        "message": f"Reservation '{reservation_id}' has been successfully cancelled. Reason: {reason}."
    }`
  },
  'agent_mcp/tools/issue_refund.py': {
    path: 'agent_mcp/tools/issue_refund.py',
    name: 'issue_refund.py',
    language: 'python',
    description: 'MCP Tool: Secure, idempotency-guarded sandbox refunds trigger.',
    content: `# agent_mcp/tools/issue_refund.py
from services.payment_service import PaymentService

def issue_refund_tool(payment_id: str, reason: str) -> dict:
    """
    MCP Tool: Trigger a safe refund on a previous transaction using PaymentService.
    """
    payment = PaymentService.get_payment_status(payment_id)
    if not payment:
        return {
            "payment_id": payment_id,
            "refund_id": "none",
            "status": "FAILED",
            "reason": reason,
            "message": f"Payment record '{payment_id}' not found."
        }
    
    payment_session_id = payment["payment_session_id"]
    amount = payment["amount"]
    
    res = PaymentService.issue_refund(payment_session_id, amount)
    
    return {
        "payment_id": payment_id,
        "refund_id": f"ref_{payment_id}",
        "status": res["status"],
        "reason": reason,
        "message": f"Refund of \${amount:.2f} processed successfully for payment '{payment_id}'."
    }`
  },
  'agent_mcp/tools/save_reservation_report.py': {
    path: 'agent_mcp/tools/save_reservation_report.py',
    name: 'save_reservation_report.py',
    language: 'python',
    description: 'MCP Tool: Compiles audit-compliant compliance checkout reports to reports/ local directory.',
    content: `# agent_mcp/tools/save_reservation_report.py
import os
import json

def save_reservation_report_tool(report_payload: dict) -> dict:
    """
    MCP Tool: Save structural JSON receipt report to the reports/ directory.
    """
    report_id = report_payload.get("report_id") or report_payload.get("reservation_id") or "report_generic"
    
    # Resolve absolute path to hospitality-reservation-payment-agent/reports
    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "reports"))
    os.makedirs(reports_dir, exist_ok=True)
    
    file_path = os.path.join(reports_dir, f"report_{report_id}.json")
    
    try:
        with open(file_path, "w") as f:
            json.dump(report_payload, f, indent=2)
        status = "SAVED"
    except Exception as e:
        status = f"FAILED: {str(e)}"
        
    return {
        "report_id": report_id,
        "file_path": f"reports/report_{report_id}.json",
        "status": status
    }`
  },
  'rag/embeddings.py': {
    path: 'rag/embeddings.py',
    name: 'embeddings.py',
    language: 'python',
    description: 'Integrates local sentence-transformers model weights to generate high-quality vector embeddings of policy documentation.',
    content: `# rag/embeddings.py
def get_text_embedding(text: str):
    """RAG Embedding service (mock for Phase 1)."""
    return [0.0] * 384`
  },
  'rag/vector_store.py': {
    path: 'rag/vector_store.py',
    name: 'vector_store.py',
    language: 'python',
    description: 'Lightweight in-memory vector indexing and search engine for RAG policy lookups.',
    content: `# rag/vector_store.py
class SimpleVectorStore:
    """Simple in-memory semantic database for policies."""
    def __init__(self):
        self.documents = []
    def add_document(self, doc_id: str, content: str, embedding: list):
        self.documents.append({"id": doc_id, "content": content, "embedding": embedding})`
  },
  'rag/retriever.py': {
    path: 'rag/retriever.py',
    name: 'retriever.py',
    language: 'python',
    description: 'Queries vector stores to locate cancellation/refund policies, passing context directly to LLM prompts.',
    content: `# rag/retriever.py
def retrieve_relevant_policies(query: str, limit: int = 2):
    """Retrieve Cancellation, Refund, or Payment policy matching keywords."""
    return ["Refund policy: 100% refund up to 24 hours prior to check-in."]`
  },
  'rag/chunking.py': {
    path: 'rag/chunking.py',
    name: 'chunking.py',
    language: 'python',
    description: 'Slices raw policy markdown files into uniform paragraphs with structural offsets.',
    content: `# rag/chunking.py
def split_markdown_into_chunks(text: str, chunk_size: int = 500) -> list:
    """Helper to slice policy markdown files into readable embedding passages."""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]`
  },
  'models/schemas.py': {
    path: 'models/schemas.py',
    name: 'schemas.py',
    language: 'python',
    description: 'Robust schemas defining structural request-response boundaries for FastAPI routes and stream endpoints.',
    content: `# models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class ReservationState(str, Enum):
    """
    Logical Workflow States of the reservation state machine.
    """
    REQUEST_RECEIVED = "REQUEST_RECEIVED"
    VALIDATED = "VALIDATED"
    AVAILABILITY_CONFIRMED = "AVAILABILITY_CONFIRMED"
    PRICE_CALCULATED = "PRICE_CALCULATED"
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PAID = "PAID"
    RESERVATION_CONFIRMED = "RESERVATION_CONFIRMED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
    FAILED = "FAILED"

class Room(BaseModel):
    """
    Business model representing a hotel room.
    """
    id: str = Field(..., example="deluxe-suite")
    name: str = Field(..., example="Deluxe Suite")
    base_price: float = Field(..., example=250.00)
    capacity: int = Field(..., example=3)

class Customer(BaseModel):
    """
    Business model representing a registered customer.
    """
    id: str = Field(..., example="cust_01")
    name: str = Field(..., example="Aquilino Francisco")
    email: str = Field(..., example="aquilino.francisco@gmail.com")

class Reservation(BaseModel):
    """
    Core Reservation Model containing transition, payment, and audit details.
    """
    reservation_id: str = Field(..., example="res_mock_8f21bc")
    customer_id: str = Field(..., example="cust_01")
    room_id: str = Field(..., example="deluxe-suite")
    reservation_state: ReservationState = Field(..., example=ReservationState.REQUEST_RECEIVED)
    payment_link: Optional[str] = Field(None, example="https://sandbox.stripe.local/pay/demo-session-001")
    payment_session_id: Optional[str] = Field(None, example="sess_mock_8f21bc")
    idempotency_key: str = Field(..., example="idem_unique_key_001")
    created_at: str = Field(..., example="2026-07-06T12:00:00Z")
    updated_at: str = Field(..., example="2026-07-06T12:00:00Z")

class Payment(BaseModel):
    """
    Business model representing a payment transaction record.
    """
    payment_id: str = Field(..., example="pay_001")
    reservation_id: str = Field(..., example="res_001")
    amount: float = Field(..., example=1250.0)
    currency: str = Field("usd", example="usd")
    status: str = Field(..., example="COMPLETED")
    payment_session_id: Optional[str] = Field(None, example="sess_001")
    created_at: str = Field(..., example="2026-07-06T10:04:00Z")
    updated_at: str = Field(..., example="2026-07-06T10:05:00Z")

# ========================================================
# API Schemas (Request/Response Envelopes)
# ========================================================

class ReservationRequest(BaseModel):
    """
    Schema for incoming reservation requests.
    """
    customer_email: str = Field(..., example="aquilino.francisco@gmail.com")
    room_type: str = Field(..., example="deluxe-suite")
    check_in: str = Field(..., example="2026-07-10")
    check_out: str = Field(..., example="2026-07-15")
    idempotency_key: str = Field(..., example="idem_unique_key_001")

class ReservationResponse(BaseModel):
    """
    Schema for standard reservation responses.
    """
    reservation_id: str = Field(..., example="res_mock_8f21bc")
    status: ReservationState = Field(..., example=ReservationState.REQUEST_RECEIVED)
    payment_link: Optional[str] = Field(None, example="https://sandbox.stripe.local/pay/demo-session-001")
    total_price: float = Field(..., example=1250.0)

class PaymentResponse(BaseModel):
    """
    Schema for standard payment query or callback responses.
    """
    payment_id: str = Field(..., example="pay_001")
    reservation_id: str = Field(..., example="res_001")
    amount: float = Field(..., example=1250.0)
    status: str = Field(..., example="COMPLETED")
    payment_link: Optional[str] = Field(None, example="https://sandbox.stripe.local/pay/demo-session-001")

class ReservationStatus(BaseModel):
    """
    Schema to describe current live workflow state transitions and status queries.
    """
    reservation_id: str = Field(..., example="res_mock_8f21bc")
    status: ReservationState = Field(..., example=ReservationState.RESERVATION_CONFIRMED)
    updated_at: str = Field(..., example="2026-07-06T12:05:00Z")
    errors: List[str] = Field(default_factory=list, example=[])`
  },
  'services/reservation_service.py': {
    path: 'services/reservation_service.py',
    name: 'reservation_service.py',
    language: 'python',
    description: 'Framework-agnostic pure business logic for room reservations and availability state changes.',
    content: `# services/reservation_service.py
import os
import json
import structlog
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = structlog.get_logger()

MOCK_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mock_data"))

def _load_json(filename: str) -> List[Any]:
    filepath = os.path.join(MOCK_DATA_DIR, filename)
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filename}", error=str(e))
        return []

def _save_json(filename: str, data: List[Any]):
    filepath = os.path.join(MOCK_DATA_DIR, filename)
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving {filename}", error=str(e))

class ReservationService:
    """
    Lightweight, mock-database driven Reservation business logic service.
    Directly reads and updates JSON datasets to demonstrate clean state separation.
    """

    @staticmethod
    def get_room(room_id: str) -> Optional[Dict[str, Any]]:
        rooms = _load_json("rooms.json")
        for r in rooms:
            if r["id"] == room_id:
                return r
        return None

    @staticmethod
    def get_customer_by_email(email: str) -> Optional[Dict[str, Any]]:
        customers = _load_json("customers.json")
        for c in customers:
            if c["email"].strip().lower() == email.strip().lower():
                return c
        return None

    @staticmethod
    def check_availability(room_id: str, check_in: str, check_out: str) -> bool:
        availability_records = _load_json("availability.json")
        for rec in availability_records:
            if rec["room_id"] == room_id and check_in <= rec["date"] < check_out:
                if not rec["available"]:
                    return False

        reservations = _load_json("reservations.json")
        for res in reservations:
            if res["room_id"] == room_id and res["reservation_state"] not in ["CANCELLED", "REFUNDED", "FAILED"]:
                if (check_in < res["check_out"]) and (check_out > res["check_in"]):
                    return False
        return True

    @staticmethod
    def create_reservation(customer_email: str, room_type: str, check_in: str, check_out: str, idempotency_key: str) -> Dict[str, Any]:
        logger.info("Service: create_reservation called", customer_email=customer_email, room_type=room_type)
        reservations = _load_json("reservations.json")
        for res in reservations:
            if res["idempotency_key"] == idempotency_key:
                return res

        customer = ReservationService.get_customer_by_email(customer_email)
        if not customer:
            customers = _load_json("customers.json")
            cust_id = f"cust_0{len(customers) + 1}"
            customer = {"id": cust_id, "name": customer_email.split("@")[0].title(), "email": customer_email}
            customers.append(customer)
            _save_json("customers.json", customers)

        is_available = ReservationService.check_availability(room_type, check_in, check_out)
        if not is_available:
            return {"reservation_id": "error", "reservation_state": "FAILED", "errors": ["Room not available for selected dates."]}

        new_res_id = f"res_00{len(reservations) + 1}"
        new_res = {
            "reservation_id": new_res_id,
            "customer_id": customer["id"],
            "room_id": room_type,
            "check_in": check_in,
            "check_out": check_out,
            "reservation_state": "REQUEST_RECEIVED",
            "payment_link": None,
            "payment_session_id": None,
            "idempotency_key": idempotency_key,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        reservations.append(new_res)
        _save_json("reservations.json", reservations)
        return new_res

    @staticmethod
    def transition_state(reservation_id: str, target_state: str) -> Dict[str, Any]:
        reservations = _load_json("reservations.json")
        for res in reservations:
            if res["reservation_id"] == reservation_id:
                res["reservation_state"] = target_state
                res["updated_at"] = datetime.utcnow().isoformat() + "Z"
                _save_json("reservations.json", reservations)
                return res
        return {"error": "Reservation not found"}

    @staticmethod
    def cancel_reservation(reservation_id: str) -> Dict[str, Any]:
        return ReservationService.transition_state(reservation_id, "CANCELLED")`
  },
  'services/payment_service.py': {
    path: 'services/payment_service.py',
    name: 'payment_service.py',
    language: 'python',
    description: 'Framework-agnostic business logic for preparing checkout links and processing transaction signals.',
    content: `# services/payment_service.py
import os
import json
import structlog
from datetime import datetime
from typing import Dict, Any, List, Optional
from services.reservation_service import _load_json, _save_json, ReservationService

logger = structlog.get_logger()

class PaymentService:
    """
    Lightweight, mock-database driven Payment business logic service.
    Directly reads and updates payment and reservation states inside JSON datasets.
    """

    @staticmethod
    def calculate_price(room_id: str, check_in: str, check_out: str) -> float:
        room = ReservationService.get_room(room_id)
        if not room:
            raise ValueError(f"Room type '{room_id}' not found.")
        try:
            date_format = "%Y-%m-%d"
            start_date = datetime.strptime(check_in, date_format)
            end_date = datetime.strptime(check_out, date_format)
            delta = end_date - start_date
            nights = max(1, delta.days)
        except Exception:
            nights = 1
        return room["base_price"] * nights

    @staticmethod
    def create_payment_link(reservation_id: str, amount: float, idempotency_key: str) -> Dict[str, Any]:
        reservations = _load_json("reservations.json")
        target_res = None
        for res in reservations:
            if res["reservation_id"] == reservation_id:
                target_res = res
                break
        if not target_res:
            raise ValueError(f"Reservation '{reservation_id}' not found.")

        payments = _load_json("payments.json")
        for pay in payments:
            if pay["reservation_id"] == reservation_id and pay["status"] == "PENDING":
                return {
                    "payment_id": pay["payment_id"],
                    "payment_link": f"https://sandbox.stripe.local/pay/demo-session-{pay['payment_session_id']}",
                    "payment_session_id": pay["payment_session_id"],
                    "status": "PENDING"
                }

        mock_sess_id = f"sess_00{len(payments) + 1}"
        mock_pay_id = f"pay_00{len(payments) + 1}"
        fake_payment_link = f"https://sandbox.stripe.local/pay/demo-session-{mock_sess_id}"

        new_payment = {
            "payment_id": mock_pay_id,
            "reservation_id": reservation_id,
            "amount": amount,
            "currency": "usd",
            "status": "PENDING",
            "payment_session_id": mock_sess_id,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        payments.append(new_payment)
        _save_json("payments.json", payments)

        target_res["reservation_state"] = "PENDING_PAYMENT"
        target_res["payment_link"] = fake_payment_link
        target_res["payment_session_id"] = mock_sess_id
        target_res["updated_at"] = datetime.utcnow().isoformat() + "Z"
        _save_json("reservations.json", reservations)

        return {
            "payment_id": mock_pay_id,
            "payment_link": fake_payment_link,
            "payment_session_id": mock_sess_id,
            "status": "PENDING"
        }

    @staticmethod
    def mark_payment_completed(payment_session_id: str) -> Dict[str, Any]:
        payments = _load_json("payments.json")
        target_payment = None
        for pay in payments:
            if pay["payment_session_id"] == payment_session_id:
                pay["status"] = "COMPLETED"
                pay["updated_at"] = datetime.utcnow().isoformat() + "Z"
                target_payment = pay
                break
        if not target_payment:
            raise ValueError(f"Payment session with id '{payment_session_id}' not found.")
        _save_json("payments.json", payments)

        reservation_id = target_payment["reservation_id"]
        ReservationService.transition_state(reservation_id, "PAID")
        ReservationService.transition_state(reservation_id, "RESERVATION_CONFIRMED")

        return {
            "payment_id": target_payment["payment_id"],
            "reservation_id": reservation_id,
            "status": "COMPLETED",
            "updated_at": target_payment["updated_at"]
        }

    @staticmethod
    def issue_refund(payment_session_id: str, amount: float) -> Dict[str, Any]:
        payments = _load_json("payments.json")
        target_payment = None
        for pay in payments:
            if pay["payment_session_id"] == payment_session_id:
                pay["status"] = "REFUNDED"
                pay["updated_at"] = datetime.utcnow().isoformat() + "Z"
                target_payment = pay
                break
        if not target_payment:
            raise ValueError(f"Completed payment session '{payment_session_id}' not found.")
        _save_json("payments.json", payments)

        ReservationService.transition_state(target_payment["reservation_id"], "REFUNDED")
        return {
            "payment_id": target_payment["payment_id"],
            "reservation_id": target_payment["reservation_id"],
            "amount_refunded": amount,
            "status": "REFUNDED"
        }
    `
  },
  'integrations/stripe/client.py': {
    path: 'integrations/stripe/client.py',
    name: 'client.py',
    language: 'python',
    description: 'Stripe Sandbox client wrapper, prepared for future direct payment integrations.',
    content: `# integrations/stripe/client.py
import structlog
from typing import Dict, Any, Optional

logger = structlog.get_logger()

class StripeSandboxClient:
    """
    Stripe Sandbox Client Wrapper.
    Reserved for future Stripe SDK integrations.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        logger.info("StripeSandboxClient initialized (placeholder mode)")

    def create_checkout_session(self, reservation_id: str, amount: float, idempotency_key: str) -> Dict[str, Any]:
        logger.info("Stripe API Wrapper: mock create_checkout_session invoked", reservation_id=reservation_id)
        return {
            "id": f"cs_test_mock_{idempotency_key[:8]}",
            "url": f"https://checkout.stripe.com/pay/mock_session_{reservation_id}",
            "amount_total": int(amount * 100),
            "currency": "usd"
        }

    def refund_payment(self, charge_id: str, amount: float, idempotency_key: str) -> Dict[str, Any]:
        logger.info("Stripe API Wrapper: mock refund_payment invoked", charge_id=charge_id)
        return {"id": f"re_test_mock_{idempotency_key[:8]}", "amount": int(amount * 100), "status": "succeeded"}`
  },
  'core/config.py': {
    path: 'core/config.py',
    name: 'config.py',
    language: 'python',
    description: 'Pydantic core application configurations and environment variables loader.',
    content: `# core/config.py
import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "Hospitality AI Agent"
    ENV: str = os.getenv("NODE_ENV", "development")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "mock_gemini_key")
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "mock_stripe_key")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "mock_webhook_secret")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()`
  },
  'core/logging.py': {
    path: 'core/logging.py',
    name: 'logging.py',
    language: 'python',
    description: 'Structured logging configuration utilizing structlog processor pipelines.',
    content: `# core/logging.py
import structlog

def setup_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )`
  },
  'mock_data/rooms.json': {
    path: 'mock_data/rooms.json',
    name: 'rooms.json',
    language: 'json',
    description: 'Mock data listing available rooms, capacity bounds, and default pricing lists.',
    content: `[
  {"id": "deluxe-suite", "name": "Deluxe Suite", "base_price": 250.00, "capacity": 3},
  {"id": "standard-queen", "name": "Standard Queen Room", "base_price": 140.00, "capacity": 2},
  {"id": "penthouse", "name": "Panoramic Penthouse", "base_price": 600.00, "capacity": 5},
  {"id": "single-cozy", "name": "Cozy Single Room", "base_price": 90.00, "capacity": 1},
  {"id": "double-comfort", "name": "Double Comfort Room", "base_price": 160.00, "capacity": 2},
  {"id": "family-suite", "name": "Spacious Family Suite", "base_price": 320.00, "capacity": 6},
  {"id": "executive-king", "name": "Executive King Room", "base_price": 210.00, "capacity": 2},
  {"id": "ocean-villa", "name": "Luxury Ocean Villa", "base_price": 750.00, "capacity": 4},
  {"id": "garden-cabin", "name": "Charming Garden Cabin", "base_price": 180.00, "capacity": 3},
  {"id": "budget-twin", "name": "Budget Twin Room", "base_price": 80.00, "capacity": 2}
]`
  },
  'mock_data/availability.json': {
    path: 'mock_data/availability.json',
    name: 'availability.json',
    language: 'json',
    description: 'Calendar table tracking room availabilities per day.',
    content: `[
  {"room_id": "deluxe-suite", "date": "2026-07-10", "available": false},
  {"room_id": "deluxe-suite", "date": "2026-07-11", "available": false},
  {"room_id": "deluxe-suite", "date": "2026-07-12", "available": false},
  {"room_id": "deluxe-suite", "date": "2026-07-13", "available": false},
  {"room_id": "deluxe-suite", "date": "2026-07-14", "available": false},
  {"room_id": "deluxe-suite", "date": "2026-07-15", "available": true},
  {"room_id": "standard-queen", "date": "2026-07-12", "available": false},
  {"room_id": "standard-queen", "date": "2026-07-13", "available": false},
  {"room_id": "standard-queen", "date": "2026-07-14", "available": true},
  {"room_id": "penthouse", "date": "2026-07-20", "available": false},
  {"room_id": "penthouse", "date": "2026-07-21", "available": false},
  {"room_id": "penthouse", "date": "2026-07-22", "available": false},
  {"room_id": "penthouse", "date": "2026-07-23", "available": false},
  {"room_id": "penthouse", "date": "2026-07-24", "available": false},
  {"room_id": "single-cozy", "date": "2026-07-15", "available": false},
  {"room_id": "single-cozy", "date": "2026-07-16", "available": false},
  {"room_id": "ocean-villa", "date": "2026-08-01", "available": false},
  {"room_id": "ocean-villa", "date": "2026-08-02", "available": false},
  {"room_id": "ocean-villa", "date": "2026-08-03", "available": false},
  {"room_id": "ocean-villa", "date": "2026-08-04", "available": false},
  {"room_id": "double-comfort", "date": "2026-07-10", "available": true},
  {"room_id": "family-suite", "date": "2026-07-10", "available": true},
  {"room_id": "executive-king", "date": "2026-07-10", "available": true}
]`
  },
  'mock_data/customers.json': {
    path: 'mock_data/customers.json',
    name: 'customers.json',
    language: 'json',
    description: 'Mock data tracking customer credentials and target notifications contact details.',
    content: `[
  {"id": "cust_01", "name": "Aquilino Francisco", "email": "aquilino.francisco@gmail.com"},
  {"id": "cust_02", "name": "Jane Doe", "email": "jane.doe@example.com"},
  {"id": "cust_03", "name": "John Smith", "email": "john.smith@example.com"},
  {"id": "cust_04", "name": "Alice Johnson", "email": "alice.johnson@example.com"},
  {"id": "cust_05", "name": "Bob Martin", "email": "bob.martin@example.com"}
]`
  },
  'mock_data/reservations.json': {
    path: 'mock_data/reservations.json',
    name: 'reservations.json',
    language: 'json',
    description: 'Active database table registering reservation records and workflow transition parameters.',
    content: `[
  {
    "reservation_id": "res_001",
    "customer_id": "cust_01",
    "room_id": "deluxe-suite",
    "check_in": "2026-07-10",
    "check_out": "2026-07-15",
    "reservation_state": "RESERVATION_CONFIRMED",
    "payment_link": "https://sandbox.stripe.local/pay/demo-session-001",
    "payment_session_id": "sess_001",
    "idempotency_key": "idem_001",
    "created_at": "2026-07-06T10:00:00Z",
    "updated_at": "2026-07-06T10:05:00Z"
  },
  {
    "reservation_id": "res_002",
    "customer_id": "cust_02",
    "room_id": "standard-queen",
    "check_in": "2026-07-12",
    "check_out": "2026-07-14",
    "reservation_state": "PENDING_PAYMENT",
    "payment_link": "https://sandbox.stripe.local/pay/demo-session-002",
    "payment_session_id": "sess_002",
    "idempotency_key": "idem_002",
    "created_at": "2026-07-06T11:00:00Z",
    "updated_at": "2026-07-06T11:02:00Z"
  },
  {
    "reservation_id": "res_003",
    "customer_id": "cust_03",
    "room_id": "penthouse",
    "check_in": "2026-07-20",
    "check_out": "2026-07-25",
    "reservation_state": "CANCELLED",
    "payment_link": null,
    "payment_session_id": null,
    "idempotency_key": "idem_003",
    "created_at": "2026-07-05T09:00:00Z",
    "updated_at": "2026-07-05T15:00:00Z"
  },
  {
    "reservation_id": "res_004",
    "customer_id": "cust_04",
    "room_id": "single-cozy",
    "check_in": "2026-07-15",
    "check_out": "2026-07-17",
    "reservation_state": "PAID",
    "payment_link": "https://sandbox.stripe.local/pay/demo-session-004",
    "payment_session_id": "sess_004",
    "idempotency_key": "idem_004",
    "created_at": "2026-07-06T08:00:00Z",
    "updated_at": "2026-07-06T08:15:00Z"
  },
  {
    "reservation_id": "res_005",
    "customer_id": "cust_05",
    "room_id": "ocean-villa",
    "check_in": "2026-08-01",
    "check_out": "2026-08-05",
    "reservation_state": "REQUEST_RECEIVED",
    "payment_link": null,
    "payment_session_id": null,
    "idempotency_key": "idem_005",
    "created_at": "2026-07-06T12:00:00Z",
    "updated_at": "2026-07-06T12:00:00Z"
  }
]`
  },
  'mock_data/payments.json': {
    path: 'mock_data/payments.json',
    name: 'payments.json',
    language: 'json',
    description: 'Secure table ledger matching Stripe transaction sessions and webhook events.',
    content: `[
  {
    "payment_id": "pay_001",
    "reservation_id": "res_001",
    "amount": 1250.0,
    "currency": "usd",
    "status": "COMPLETED",
    "payment_session_id": "sess_001",
    "created_at": "2026-07-06T10:04:00Z",
    "updated_at": "2026-07-06T10:05:00Z"
  },
  {
    "payment_id": "pay_002",
    "reservation_id": "res_002",
    "amount": 280.0,
    "currency": "usd",
    "status": "PENDING",
    "payment_session_id": "sess_002",
    "created_at": "2026-07-06T11:02:00Z",
    "updated_at": "2026-07-06T11:02:00Z"
  },
  {
    "payment_id": "pay_003",
    "reservation_id": "res_003",
    "amount": 3000.0,
    "currency": "usd",
    "status": "REFUNDED",
    "payment_session_id": "sess_003",
    "created_at": "2026-07-05T09:10:00Z",
    "updated_at": "2026-07-05T15:00:00Z"
  },
  {
    "payment_id": "pay_004",
    "reservation_id": "res_004",
    "amount": 180.0,
    "currency": "usd",
    "status": "COMPLETED",
    "payment_session_id": "sess_004",
    "created_at": "2026-07-06T08:14:00Z",
    "updated_at": "2026-07-06T08:15:00Z"
  },
  {
    "payment_id": "pay_005",
    "reservation_id": "res_005",
    "amount": 3000.0,
    "currency": "usd",
    "status": "PENDING",
    "payment_session_id": "sess_005",
    "created_at": "2026-07-06T12:00:00Z",
    "updated_at": "2026-07-06T12:00:00Z"
  }
]`
  },
  'knowledge_base/cancellation_policy.md': {
    path: 'knowledge_base/cancellation_policy.md',
    name: 'cancellation_policy.md',
    language: 'markdown',
    description: 'Corporate rules for late cancellations, penalties, and calendar adjustments.',
    content: `# Cancellation Policy

1. Reservations can be cancelled free of charge up to 48 hours prior to check-in (14:00 local time).
2. Cancellations between 48 and 24 hours incur a 50% reservation penalty.
3. No-shows or cancellations within 24 hours are charged at 100% room rate.`
  },
  'knowledge_base/refund_policy.md': {
    path: 'knowledge_base/refund_policy.md',
    name: 'refund_policy.md',
    language: 'markdown',
    description: 'Mandates detailing transaction methods, idempotency rules, and approval sequences for sandbox refunds.',
    content: `# Refund Policy

1. Approved refunds are processed directly via the Stripe Sandbox back to the original funding source.
2. All refunds require an associated \`idempotency_key\` and reference payment tracking identifier.
3. Refunds may take 5-10 business days to reflect in production accounts, though sandbox refunds execute immediately.`
  },
  'knowledge_base/payment_policy.md': {
    path: 'knowledge_base/payment_policy.md',
    name: 'payment_policy.md',
    language: 'markdown',
    description: 'Protocols instructing the conversational engine to never touch credit card details, but redirect to safe checkout sessions.',
    content: `# Payment Policy

1. All transactions require upfront authorization.
2. The AI Agent NEVER takes credit card information directly in the conversation; a checkout payment link is served.
3. An active Stripe Checkout Session must complete before reservation status is confirmed.`
  },
  'knowledge_base/hotel_terms.md': {
    path: 'knowledge_base/hotel_terms.md',
    name: 'hotel_terms.md',
    language: 'markdown',
    description: 'Official guest instructions, check-in bounds, incidentals policies, and occupancy limits.',
    content: `# Hotel Terms and Conditions

- Check-in time is 15:00. Check-out is 11:00.
- Government-issued photo identification and credit card hold for incidentals are required at check-in.
- Maximum occupancy rules per room type must be strictly followed.`
  },
  'docs/architecture.md': {
    path: 'docs/architecture.md',
    name: 'architecture.md',
    language: 'markdown',
    description: 'Comprehensive, high-level summary of the service stack (FastAPI, LangGraph, CrewAI, MCP, RAG).',
    content: `# Architecture Overview

This portfolio showcases an **AI Agentic platform** designed to solve hotel reservations and secure payments with a safe, fully-auditable sandbox workflow.

## Component Stack
- **FastAPI**: Gateway microservice serving REST APIs, webhook receivers, and real-time Server-Sent Events (SSE) updates.
- **Services Layer**: Framework-agnostic pure business logic for core reservations and payment workflows.
- **Integrations Layer**: Safe sandbox API client wrappers (such as Stripe Sandbox wrappers) with zero hardcoded credentials or initialization side-effects.
- **Core Package**: Application config parsing and structured logging setups.
- **LangGraph**: Workflow engine routing state validations, room scheduling checks, and price calculators.
- **CrewAI**: Orchestrator containing two specialized task agents: \`ReservationAgent\` and \`PaymentAgent\`.
- **MCP-Style Tools**: Encapsulated system interfaces exposing database actions, price calculations, and checkout sessions to agents.
- **Local RAG**: Context-aware retrieval engine that injects hotel reservation, refund, and cancellation policies into the workflow.`
  },
  'docs/payment-flow.md': {
    path: 'docs/payment-flow.md',
    name: 'payment-flow.md',
    language: 'markdown',
    description: 'System details detailing transaction integrity, webhook bindings, and human verification checkpoints.',
    content: `# Stripe Sandbox Payment Flow

We adhere to rigorous **auditable payment security principles**:

1. **Indirect Charging**: Agents never handle primary card holder data directly. The agent generates a checkout link.
2. **Checkout Sandbox**: Payment is completed in Stripe Sandbox.
3. **Idempotency Key Verification**: Every transactional session includes an \`idempotency_key\` to avoid duplicate billing.
4. **Webhook Source of Truth**: Success state transitions are exclusively driven by Stripe webhook callbacks (\`checkout.session.completed\`), not frontend clients.
5. **Human-in-the-Loop**: Confirmations are explicitly required prior to locking down reservations and issuing payouts.`
  },
  'docs/mcp.md': {
    path: 'docs/mcp.md',
    name: 'mcp.md',
    language: 'markdown',
    description: 'Specifications details for the Model Context Protocol tools schema exposed by Python.',
    content: `# Model Context Protocol (MCP) Integration

Our architecture implements an MCP-style tool server (\`agent_mcp/server.py\`) that decouples business tooling from agent prompt execution:

### Available Tools:
- \`check_availability\`: Query dates and room types.
- \`calculate_price\`: Compute nights and rates.
- \`create_payment_link\`: Secure connection with Stripe sandbox to produce active checkout checkout URLs.
- \`check_payment_status\`: Query session state.
- \`confirm_reservation\`: Finalize state changes upon validated payments.
- \`cancel_reservation\`: Release booked inventory.
- \`issue_refund\`: Direct Stripe Sandbox refund trigger.
- \`save_reservation_report\`: Compile final compliance JSON files into the \`reports/\` folder.`
  },
  'docs/rag.md': {
    path: 'docs/rag.md',
    name: 'rag.md',
    language: 'markdown',
    description: 'Design choices explaining policy chunkings, semantic embeddings, and LLM context injections.',
    content: `# Local RAG Knowledge Retrieval

To make our reservation specialists compliant with legal guidelines and local policies, a lightweight Local RAG module (\`rag/\`) is integrated:

### Document Storage:
Policies in \`knowledge_base/\` are chunked and embedded:
- \`cancellation_policy.md\`
- \`refund_policy.md\`
- \`payment_policy.md\`
- \`hotel_terms.md\`

### Retrieval Flow:
Before calculating checkout parameters or deciding on cancellations, the system queries embeddings. The retrieved contextual passages are appended to the LangGraph/CrewAI context limits.`
  },
  'docs/langgraph.md': {
    path: 'docs/langgraph.md',
    name: 'langgraph.md',
    language: 'markdown',
    description: 'Graph visualization and markdown maps explaining checkout state-evaluators.',
    content: `# LangGraph Workflow Orchestration

Our platform utilizes **LangGraph** as a deterministic, state-driven workflow coordinator. This layer guarantees that reservation requests are systematically validated, verified, priced, and processed prior to initiating payments or involving downstream human-like agents (e.g. CrewAI specialists).

---

## The Core Design Philosophy

### Decoupling Orchestration from Execution

A fundamental architectural constraint of this platform is that **LangGraph nodes are strictly coordinators (orchestrators)**. They do NOT execute business logic, write database records, calculate financial numbers, or handle third-party SDK calls. 

Instead, LangGraph maintains and transitions thread state, making RPC-style tool-calls to the **Model Context Protocol (MCP)** tool layer.

#### Why this separation is vital:
1. **Separation of Concerns:** Keep routing logic separated from core application rules.
2. **Reusability:** Business tools can be called by diverse interfaces (REST APIs, CLI, CrewAI agents, or LangGraph) identically.
3. **Auditability:** Every system transition and API/tool call logs structured events, making failure analysis straightforward.
4. **Deterministic Gatekeeping:** Ensuring that expensive operations are only reached if previous validations pass.

---

## State Definition (\`ReservationState\`)

The state of our workflow is tracked inside a standard \`TypedDict\` containing transaction-specific fields:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| \`reservation_id\` | \`Optional[str]\` | The unique system identifier for the reservation. Generated on demand if missing. |
| \`customer_id\` | \`Optional[str]\` | Identifier tracking the requesting guest. |
| \`room_id\` | \`Optional[str]\` | The selected room category code (e.g. \`"deluxe-suite"\`). |
| \`check_in\` | \`Optional[str]\` | Check-in date formatted as \`YYYY-MM-DD\`. |
| \`check_out\` | \`Optional[str]\` | Check-out date formatted as \`YYYY-MM-DD\`. |
| \`guests\` | \`Optional[int]\` | Count of staying guests. |
| \`reservation_state\` | \`Optional[str]\` | Orchestrated stage status (e.g. \`"VALIDATED"\`, \`"AVAILABILITY_CONFIRMED"\`, \`"PRICE_CALCULATED"\`, \`"PENDING_PAYMENT"\`, \`"FAILED"\`). |
| \`payment_state\` | \`Optional[str]\` | Current transaction checkout state (e.g. \`"PENDING"\`, \`"PAID"\`). |
| \`payment_link\` | \`Optional[str]\` | The generated Stripe Checkout sandbox transaction URL. |
| \`payment_id\` | \`Optional[str]\` | Sandbox payment transaction reference. |
| \`total_price\` | \`Optional[float]\`| The calculated reservation cost subtotal. |
| \`currency\` | \`Optional[str]\` | ISO currency code (e.g. \`"usd"\`). |
| \`messages\` | \`List[str]\` | Sequential list of user-facing status messages appended throughout execution. |
| \`error\` | \`Optional[str]\` | Detailed explanation of error if a node or tool execution fails. |

---

## Workflow Graph Nodes

The graph comprises 5 sequential nodes:

\`\`\`
[START]
   │
   ▼
[validate_request] ──(fail)──► [END]
   │ (pass)
   ▼
[check_availability] ──(fail)──► [END]
   │ (pass)
   ▼
[calculate_price] ──(fail)──► [END]
   │ (pass)
   ▼
[create_payment_link] ──(fail)──► [END]
   │ (pass)
   ▼
[finish]
   │
   ▼
[END]
\`\`\`

### 1. \`validate_request\`
- **Role:** Exercises structural format checks on inputs (ensures customer IDs, room IDs, check-in, check-out, and guests count are provided and logically consistent).
- **Result:** Transitions \`reservation_state\` to \`"VALIDATED"\` or \`"FAILED"\`.

### 2. \`check_availability\`
- **Role:** Invokes the \`check_availability\` MCP tool to query rooms inventory.
- **Result:** Transitions \`reservation_state\` to \`"AVAILABILITY_CONFIRMED"\` or \`"FAILED"\`.

### 3. \`calculate_price\`
- **Role:** Invokes the \`calculate_price\` MCP tool to compute price tiers.
- **Result:** Transitions \`reservation_state\` to \`"PRICE_CALCULATED"\` or \`"FAILED"\`.

### 4. \`create_payment_link\`
- **Role:** Invokes the \`create_payment_link\` MCP tool to register payment references.
- **Result:** Transitions \`reservation_state\` to \`"PENDING_PAYMENT"\` or \`"FAILED"\`.

### 5. \`finish\`
- **Role:** Finalizes successful workflow executions and appends a completion status.
- **Result:** Transitions state safely to \`END\`.

---

## Conditional Routing & Decision Edges

Deterministic branching is governed by checking the state's \`reservation_state\` flag at each node exit point. If any step assigns \`"FAILED"\`, the graph skips remaining operations and immediately routes to \`END\`.

### Routing Logic:

- **After \`validate_request\`:**
  - \`FAILED\` ➔ \`END\`
  - \`VALIDATED\` ➔ \`check_availability\`

- **After \`check_availability\`:**
  - \`FAILED\` ➔ \`END\`
  - \`AVAILABILITY_CONFIRMED\` ➔ \`calculate_price\`

- **After \`calculate_price\`:**
  - \`FAILED\` ➔ \`END\`
  - \`PRICE_CALCULATED\` ➔ \`create_payment_link\`

- **After \`create_payment_link\`:**
  - \`FAILED\` ➔ \`END\`
  - \`PENDING_PAYMENT\` ➔ \`finish\`
`
  },
  'docs/interview-notes.md': {
    path: 'docs/interview-notes.md',
    name: 'interview-notes.md',
    language: 'markdown',
    description: 'Cheat sheets and architecture designs optimized for Technical System Design presentations.',
    content: `# System Design Interview Prep

This repository is optimized for technical system design demonstrations:

### Key Talking Points:
1. **Security**: Zero access to credit card detail inside the LLM prompt. Exclusively handles tokenized Sandbox session IDs.
2. **Idempotency**: How Stripe idempotency keys protect the system from network retry issues.
3. **State Consistency**: Decoupled REST routes where state can only transition to \`PAID\` via webhook signatures.
4. **Agent-Tool Separation**: Decoupling tool logical implementations using MCP servers.`
  },
  'requirements.txt': {
    path: 'requirements.txt',
    name: 'requirements.txt',
    language: 'toml',
    description: 'Defines direct package requirements for the target Python environment.',
    content: `fastapi>=0.100.0
uvicorn>=0.22.0
langgraph>=0.1.0
crewai>=0.28.0
stripe>=6.0.0
pydantic>=2.0
mcp>=1.0.0
numpy>=1.24.0
sentence-transformers>=2.2.0
python-dotenv>=1.0.0
structlog>=23.1.0`
  },
  'pyproject.toml': {
    path: 'pyproject.toml',
    name: 'pyproject.toml',
    language: 'toml',
    description: 'Poetry project configurations, setting dependencies, author specs, and packaging details.',
    content: `[tool.poetry]
name = "hospitality-reservation-payment-agent"
version = "0.1.0"
description = "AI Agentic Platform for Hotel Reservations and Payments with a safe, auditable payment workflow."
authors = ["Aquilino Francisco <aquilino.francisco@gmail.com>"]
readme = "README.md"
package-mode = false

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.111.0"
uvicorn = "^0.30.1"
langgraph = "^0.1.4"
crewai = "^0.32.0"
stripe = "^9.10.0"
pydantic = "^2.7.4"
structlog = "^24.1.0"
python-dotenv = "^1.0.1"
sentence-transformers = "^3.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"`
  },
  'Dockerfile': {
    path: 'Dockerfile',
    name: 'Dockerfile',
    language: 'dockerfile',
    description: 'Docker image blueprint building the target python stack and starting FastAPI gateway.',
    content: `FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`
  },
  'docker-compose.yml': {
    path: 'docker-compose.yml',
    name: 'docker-compose.yml',
    language: 'yaml',
    description: 'Orchestrates the FastAPI service container, mapping credentials and volume binds.',
    content: `version: '3.8'

services:
  agent-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - STRIPE_SECRET_KEY=\${STRIPE_SECRET_KEY}
      - STRIPE_WEBHOOK_SECRET=\${STRIPE_WEBHOOK_SECRET}
      - GEMINI_API_KEY=\${GEMINI_API_KEY}
    volumes:
      - .:/app
    restart: always`
  },
  '.env.example': {
    path: '.env.example',
    name: '.env.example',
    language: 'ini',
    description: 'Guides configuring Stripe API secrets, Webhooks endpoints, and Gemini keys locally without leakage.',
    content: `# Core Configuration
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO

# API Keys (Do not commit real keys!)
GEMINI_API_KEY=your_gemini_api_key_here
STRIPE_SECRET_KEY=sk_test_your_stripe_sandbox_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_stripe_webhook_secret_here

# App URL
APP_URL=https://your-app-domain.com`
  },
  '.gitignore': {
    path: '.gitignore',
    name: '.gitignore',
    language: 'ini',
    description: 'Instructs git to ignore local caches, log sheets, and .env files containing API keys.',
    content: `# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environments
.env
.venv
venv/
ENV/
env.bak/
venv.bak/

# Logs and databases
*.log
local_db/

# OS metadata
.DS_Store
Thumbs.db

# Project-specific
reports/*.pdf
reports/*.json
!reports/.gitkeep`
  },
  'README.md': {
    path: 'README.md',
    name: 'README.md',
    language: 'markdown',
    description: 'The root presentation index, detailing key features, installation sequences, and file structures.',
    content: `# Hospitality Reservation & Payment AI Agent Platform

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green.svg)](https://fastapi.tiangolo.com)
[![Stripe Sandbox](https://img.shields.io/badge/Stripe-Sandbox-635BFF.svg)](https://stripe.com)

An elegant agentic system engineered for **secured, auditable room reservation checkouts** using **LangGraph**, **CrewAI**, **MCP tools**, and **Stripe Sandbox integrations**.

> 💡 *Note: This repository is structured as a premium technical portfolio presentation for system design and advanced engineering showcases.*

## 🚀 Key Architectural Principles
- **Indirect Checkout Integration**: The conversational AI NEVER holds or requests primary cardholder numbers directly in raw inputs.
- **Strict Webhook Source of Truth**: State machine transitions are entirely driven by cryptographically-verified Stripe signature events (\`checkout.session.completed\`).
- **Decoupled Business Services**: Multi-Agent configurations invoke external actions through standard MCP (Model Context Protocol) specifications.
- **Idempotent Operations**: All workflows must provide unique idempotency keys before executing a sandbox transaction.

---

## 📂 Repository Layout
- \`app/\`: FastAPI controllers, routers, SSE endpoints, and webhooks.
- \`services/\`: Lightweight business logic layer (completely decoupled from frameworks and transport layers).
- \`integrations/\`: Third-party integration packages (e.g., Stripe Sandbox API client).
- \`core/\`: Application settings, environment configuration, and structured logging.
- \`graph/\`: LangGraph definitions specifying state transitions and policy evaluations.
- \`crew/\`: CrewAI execution parameters (ReservationAgent & PaymentAgent specifications).
- \`agent_mcp/\`: decoupled tools and server configuration for Agent-System actions.
- \`rag/\`: semantic lookup module querying in-memory vectors.
- \`knowledge_base/\`: policy guidelines in pure markdown.
- \`models/\`: pydantic validation schemas.
- \`mock_data/\`: lightweight database presets.

---

## 🛠️ Step-by-Step Installation

### Prerequisites
- **Python 3.11+**
- **Docker** and **Docker-compose** (Optional)

### Local Configuration
1. Clone the repository:
   \`\`\`bash
   git clone https://github.com/aquilinoFrancisco/hospitality-reservation-payment-agent.git
   cd hospitality-reservation-payment-agent
   \`\`\`
2. Set up virtual environment and install dependencies:
   \`\`\`bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   \`\`\`
3. Set your credentials:
   \`\`\`bash
   cp .env.example .env
   # Modify values in .env safely
   \`\`\`
4. Start development server:
   \`\`\`bash
   uvicorn app.main:app --reload --port 8000
   \`\`\`

---

## 🔗 Live Architecture Documentation
For deep-dives into each module's code structure and detailed system flowcharts:
- [Architecture Blueprint](./docs/architecture.md)
- [Stripe Sandbox Flow](./docs/payment-flow.md)
- [Model Context Protocol Integration](./docs/mcp.md)
- [Local RAG Design](./docs/rag.md)
- [LangGraph Routing Diagrams](./docs/langgraph.md)
- [System Design Interview Reference Sheets](./docs/interview-notes.md)`
  }
};

export const REPO_TREE: FolderNode[] = [
  {
    name: 'hospitality-reservation-payment-agent',
    path: '',
    type: 'folder',
    children: [
      {
        name: 'app',
        path: 'app',
        type: 'folder',
        children: [
          { name: '__init__.py', path: 'app/__init__.py', type: 'file' },
          { name: 'main.py', path: 'app/main.py', type: 'file' },
          { name: 'dependencies.py', path: 'app/dependencies.py', type: 'file' },
          {
            name: 'api',
            path: 'app/api',
            type: 'folder',
            children: [
              { name: '__init__.py', path: 'app/api/__init__.py', type: 'file' },
              { name: 'routes.py', path: 'app/api/routes.py', type: 'file' },
              { name: 'stream.py', path: 'app/api/stream.py', type: 'file' },
              { name: 'webhooks.py', path: 'app/api/webhooks.py', type: 'file' },
            ]
          }
        ]
      },
      {
        name: 'services',
        path: 'services',
        type: 'folder',
        children: [
          { name: '__init__.py', path: 'services/__init__.py', type: 'file' },
          { name: 'reservation_service.py', path: 'services/reservation_service.py', type: 'file' },
          { name: 'payment_service.py', path: 'services/payment_service.py', type: 'file' },
        ]
      },
      {
        name: 'integrations',
        path: 'integrations',
        type: 'folder',
        children: [
          { name: '__init__.py', path: 'integrations/__init__.py', type: 'file' },
          {
            name: 'stripe',
            path: 'integrations/stripe',
            type: 'folder',
            children: [
              { name: '__init__.py', path: 'integrations/stripe/__init__.py', type: 'file' },
              { name: 'client.py', path: 'integrations/stripe/client.py', type: 'file' },
            ]
          }
        ]
      },
      {
        name: 'core',
        path: 'core',
        type: 'folder',
        children: [
          { name: '__init__.py', path: 'core/__init__.py', type: 'file' },
          { name: 'config.py', path: 'core/config.py', type: 'file' },
          { name: 'logging.py', path: 'core/logging.py', type: 'file' },
        ]
      },
      {
        name: 'graph',
        path: 'graph',
        type: 'folder',
        children: [
          { name: '__init__.py', path: 'graph/__init__.py', type: 'file' },
          { name: 'state.py', path: 'graph/state.py', type: 'file' },
          { name: 'workflow.py', path: 'graph/workflow.py', type: 'file' },
        ]
      },
      {
        name: 'crew',
        path: 'crew',
        type: 'folder',
        children: [
          { name: '__init__.py', path: 'crew/__init__.py', type: 'file' },
          { name: 'reservation_agent.py', path: 'crew/reservation_agent.py', type: 'file' },
          { name: 'payment_agent.py', path: 'crew/payment_agent.py', type: 'file' },
          { name: 'tasks.py', path: 'crew/tasks.py', type: 'file' },
          { name: 'hospitality_crew.py', path: 'crew/hospitality_crew.py', type: 'file' },
        ]
      },
      {
        name: 'agent_mcp',
        path: 'agent_mcp',
        type: 'folder',
        children: [
          { name: '__init__.py', path: 'agent_mcp/__init__.py', type: 'file' },
          { name: 'server.py', path: 'agent_mcp/server.py', type: 'file' },
          {
            name: 'tools',
            path: 'agent_mcp/tools',
            type: 'folder',
            children: [
              { name: '__init__.py', path: 'agent_mcp/tools/__init__.py', type: 'file' },
              { name: 'check_availability.py', path: 'agent_mcp/tools/check_availability.py', type: 'file' },
              { name: 'calculate_price.py', path: 'agent_mcp/tools/calculate_price.py', type: 'file' },
              { name: 'create_payment_link.py', path: 'agent_mcp/tools/create_payment_link.py', type: 'file' },
              { name: 'check_payment_status.py', path: 'agent_mcp/tools/check_payment_status.py', type: 'file' },
              { name: 'confirm_reservation.py', path: 'agent_mcp/tools/confirm_reservation.py', type: 'file' },
              { name: 'cancel_reservation.py', path: 'agent_mcp/tools/cancel_reservation.py', type: 'file' },
              { name: 'issue_refund.py', path: 'agent_mcp/tools/issue_refund.py', type: 'file' },
              { name: 'save_reservation_report.py', path: 'agent_mcp/tools/save_reservation_report.py', type: 'file' },
            ]
          }
        ]
      },
      {
        name: 'rag',
        path: 'rag',
        type: 'folder',
        children: [
          { name: '__init__.py', path: 'rag/__init__.py', type: 'file' },
          { name: 'embeddings.py', path: 'rag/embeddings.py', type: 'file' },
          { name: 'vector_store.py', path: 'rag/vector_store.py', type: 'file' },
          { name: 'retriever.py', path: 'rag/retriever.py', type: 'file' },
          { name: 'chunking.py', path: 'rag/chunking.py', type: 'file' },
        ]
      },
      {
        name: 'models',
        path: 'models',
        type: 'folder',
        children: [
          { name: '__init__.py', path: 'models/__init__.py', type: 'file' },
          { name: 'schemas.py', path: 'models/schemas.py', type: 'file' },
        ]
      },
      {
        name: 'mock_data',
        path: 'mock_data',
        type: 'folder',
        children: [
          { name: 'rooms.json', path: 'mock_data/rooms.json', type: 'file' },
          { name: 'availability.json', path: 'mock_data/availability.json', type: 'file' },
          { name: 'customers.json', path: 'mock_data/customers.json', type: 'file' },
          { name: 'reservations.json', path: 'mock_data/reservations.json', type: 'file' },
          { name: 'payments.json', path: 'mock_data/payments.json', type: 'file' },
        ]
      },
      {
        name: 'knowledge_base',
        path: 'knowledge_base',
        type: 'folder',
        children: [
          { name: 'cancellation_policy.md', path: 'knowledge_base/cancellation_policy.md', type: 'file' },
          { name: 'refund_policy.md', path: 'knowledge_base/refund_policy.md', type: 'file' },
          { name: 'payment_policy.md', path: 'knowledge_base/payment_policy.md', type: 'file' },
          { name: 'hotel_terms.md', path: 'knowledge_base/hotel_terms.md', type: 'file' },
        ]
      },
      {
        name: 'reports',
        path: 'reports',
        type: 'folder',
        children: [
          { name: '.gitkeep', path: 'reports/.gitkeep', type: 'file' }
        ]
      },
      {
        name: 'logs',
        path: 'logs',
        type: 'folder',
        children: [
          { name: '.gitkeep', path: 'logs/.gitkeep', type: 'file' }
        ]
      },
      {
        name: 'tests',
        path: 'tests',
        type: 'folder',
        children: [
          { name: '.gitkeep', path: 'tests/.gitkeep', type: 'file' }
        ]
      },
      {
        name: 'docs',
        path: 'docs',
        type: 'folder',
        children: [
          { name: 'architecture.md', path: 'docs/architecture.md', type: 'file' },
          { name: 'payment-flow.md', path: 'docs/payment-flow.md', type: 'file' },
          { name: 'mcp.md', path: 'docs/mcp.md', type: 'file' },
          { name: 'rag.md', path: 'docs/rag.md', type: 'file' },
          { name: 'langgraph.md', path: 'docs/langgraph.md', type: 'file' },
          { name: 'interview-notes.md', path: 'docs/interview-notes.md', type: 'file' },
        ]
      },
      { name: '.env.example', path: '.env.example', type: 'file' },
      { name: '.gitignore', path: '.gitignore', type: 'file' },
      { name: 'requirements.txt', path: 'requirements.txt', type: 'file' },
      { name: 'pyproject.toml', path: 'pyproject.toml', type: 'file' },
      { name: 'Dockerfile', path: 'Dockerfile', type: 'file' },
      { name: 'docker-compose.yml', path: 'docker-compose.yml', type: 'file' },
      { name: 'README.md', path: 'README.md', type: 'file' }
    ]
  }
];

export const MOCK_RAG_DATABASE = [
  {
    doc: 'cancellation_policy.md',
    title: 'Cancellation Policy',
    content: 'Reservations can be cancelled free of charge up to 48 hours prior to check-in (14:00 local time). Cancellations between 48 and 24 hours incur a 50% reservation penalty. No-shows or cancellations within 24 hours are charged at 100% room rate.',
    tags: ['cancel', 'cancellation', 'penalty', 'late', 'hours', 'fees']
  },
  {
    doc: 'refund_policy.md',
    title: 'Refund Policy',
    content: 'Approved refunds are processed directly via the Stripe Sandbox back to the original funding source. All refunds require an associated idempotency_key and reference payment tracking identifier. Refunds may take 5-10 business days to reflect in production accounts.',
    tags: ['refund', 'money', 'chargeback', 'stripe', 'return', 'reimbursement', 'days']
  },
  {
    doc: 'payment_policy.md',
    title: 'Payment Policy',
    content: 'All transactions require upfront authorization. The AI Agent NEVER takes credit card information directly in the conversation; a checkout payment link is served. An active Stripe Checkout Session must complete before reservation status is confirmed.',
    tags: ['payment', 'charge', 'credit card', 'stripe', 'checkout', 'security', 'secure']
  },
  {
    doc: 'hotel_terms.md',
    title: 'Hotel Terms & Conditions',
    content: 'Check-in time is 15:00. Check-out is 11:00. Government-issued photo identification and credit card hold for incidentals are required at check-in. Maximum occupancy rules per room type must be strictly followed.',
    tags: ['terms', 'check-in', 'check-out', 'occupancy', 'id', 'deposit', 'hold', 'incidentals']
  }
];
