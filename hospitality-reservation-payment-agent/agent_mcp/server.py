# agent_mcp/server.py
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
            return {"error": error_msg, "status": "FAILED"}
