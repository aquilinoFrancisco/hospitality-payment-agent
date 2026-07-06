# agent_mcp/server.py
"""
Simple MCP-style tool registry.

This server exposes controlled business tools to agents.

Important:
Agents do not access repositories, services, Stripe, Conekta or Mercado Pago
directly. They only call registered MCP tools through this registry.
"""

from __future__ import annotations

from typing import Any, Dict, List

import structlog

from agent_mcp.tools import (
    calculate_price_tool,
    cancel_reservation_tool,
    check_availability_tool,
    check_payment_status_tool,
    confirm_reservation_tool,
    create_payment_link_tool,
    issue_refund_tool,
    save_reservation_report_tool,
)

logger = structlog.get_logger()


class MCPServer:
    """
    Simple Model Context Protocol-style server registry.

    It routes agent tool-calls to deterministic business tools.
    """

    def __init__(self) -> None:
        self._registry = {
            "check_availability": check_availability_tool,
            "calculate_price": calculate_price_tool,
            "create_payment_link": create_payment_link_tool,
            "check_payment_status": check_payment_status_tool,
            "confirm_reservation": confirm_reservation_tool,
            "cancel_reservation": cancel_reservation_tool,
            "issue_refund": issue_refund_tool,
            "save_reservation_report": save_reservation_report_tool,
        }

        logger.info(
            "mcp_server_registry_initialized",
            registered_tools=list(self._registry.keys()),
        )

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List metadata for all registered MCP tools.
        """

        return [
            {
                "name": "check_availability",
                "description": (
                    "Checks room availability within check-in and check-out dates."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "room_id": {"type": "string"},
                        "check_in": {"type": "string"},
                        "check_out": {"type": "string"},
                    },
                    "required": ["room_id", "check_in", "check_out"],
                },
            },
            {
                "name": "calculate_price",
                "description": (
                    "Calculates room price based on dates, room type and guests."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "room_id": {"type": "string"},
                        "check_in": {"type": "string"},
                        "check_out": {"type": "string"},
                        "guests": {"type": "integer"},
                    },
                    "required": [
                        "room_id",
                        "check_in",
                        "check_out",
                        "guests",
                    ],
                },
            },
            {
                "name": "create_payment_link",
                "description": (
                    "Creates a safe payment link using the configured provider. "
                    "Supported providers: stripe, conekta, mercado_pago."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "reservation_id": {"type": "string"},
                        "amount": {"type": "number"},
                        "currency": {"type": "string"},
                        "provider": {
                            "type": "string",
                            "enum": [
                                "stripe",
                                "conekta",
                                "mercado_pago",
                            ],
                        },
                    },
                    "required": ["reservation_id", "amount"],
                },
            },
            {
                "name": "check_payment_status",
                "description": (
                    "Checks transaction status for a specific payment ID."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "payment_id": {"type": "string"},
                    },
                    "required": ["payment_id"],
                },
            },
            {
                "name": "confirm_reservation",
                "description": (
                    "Confirms and activates a reservation after payment "
                    "confirmation."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "reservation_id": {"type": "string"},
                    },
                    "required": ["reservation_id"],
                },
            },
            {
                "name": "cancel_reservation",
                "description": (
                    "Cancels a reservation and releases the room calendar block."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "reservation_id": {"type": "string"},
                        "reason": {"type": "string"},
                    },
                    "required": ["reservation_id", "reason"],
                },
            },
            {
                "name": "issue_refund",
                "description": (
                    "Requests a safe refund through the original payment "
                    "provider when possible."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "payment_id": {"type": "string"},
                        "reason": {"type": "string"},
                        "provider": {
                            "type": "string",
                            "enum": [
                                "stripe",
                                "conekta",
                                "mercado_pago",
                            ],
                        },
                    },
                    "required": ["payment_id", "reason"],
                },
            },
            {
                "name": "save_reservation_report",
                "description": (
                    "Saves a structured JSON report for a reservation workflow."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "report_payload": {"type": "object"},
                    },
                    "required": ["report_payload"],
                },
            },
        ]

    def call_tool(
        self,
        tool_name: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute a registered tool by name.
        """

        logger.info(
            "mcp_call_tool_triggered",
            tool_name=tool_name,
            arguments=kwargs,
        )

        tool_func = self._registry.get(tool_name)

        if not tool_func:
            error_message = f"Tool '{tool_name}' is not registered."

            logger.error(
                "mcp_tool_not_registered",
                tool_name=tool_name,
            )

            return {
                "error": error_message,
                "status": "FAILED",
            }

        try:
            result = tool_func(**kwargs)

            logger.info(
                "mcp_tool_execution_successful",
                tool_name=tool_name,
            )

            return result

        except Exception as exc:
            error_message = (
                f"Failed to execute tool '{tool_name}': {str(exc)}"
            )

            logger.exception(
                "mcp_tool_execution_failed",
                tool_name=tool_name,
            )

            return {
                "error": error_message,
                "status": "FAILED",
            }