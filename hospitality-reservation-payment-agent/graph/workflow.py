# graph/workflow.py
"""
LangGraph reservation workflow.

Sprint 6A flow:

request_received
    -> validate_request
    -> check_availability
    -> calculate_price
    -> retrieve_policy
    -> generate_llm_summary
    -> create_payment_link
    -> finish
    -> END

The workflow intentionally stops in PENDING_PAYMENT.

Payment confirmation must be handled by a separate webhook-driven workflow.
The agent must never mark a payment as completed by itself.
"""

from __future__ import annotations

import datetime
import json
import os
import sys
import uuid
from typing import Any

import structlog
from langgraph.graph import END, StateGraph

# Allows direct execution with:
# python graph/workflow.py
PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from agent_mcp.server import MCPServer
from core.config import settings
from graph.llm_router import LLMRouter
from graph.prompts import RESERVATION_STATUS_PROMPT, SYSTEM_PROMPT
from graph.state import ReservationState
from rag.retriever import create_retriever

logger = structlog.get_logger()
mcp_server = MCPServer()


def _now() -> str:
    """
    Return the current UTC timestamp in ISO-8601 format.
    """
    return datetime.datetime.now(
        datetime.timezone.utc,
    ).isoformat()


def _ensure_state_collections(
    state: ReservationState,
) -> None:
    """
    Ensure mutable state collections exist before a node uses them.
    """
    state.setdefault("messages", [])
    state.setdefault("execution_trace", [])


def _trace(
    state: ReservationState,
    node_name: str,
    status: str,
    **metadata: Any,
) -> None:
    """
    Append an auditable node execution record to the workflow state.
    """
    _ensure_state_collections(state)

    trace_entry: dict[str, Any] = {
        "node": node_name,
        "status": status,
        "timestamp": _now(),
    }

    if metadata:
        trace_entry["metadata"] = metadata

    state["execution_trace"].append(trace_entry)


def _fail_state(
    state: ReservationState,
    node_name: str,
    error: str,
) -> ReservationState:
    """
    Apply the standard workflow failure contract.
    """
    _ensure_state_collections(state)

    state["reservation_state"] = "FAILED"
    state["error"] = error
    state["messages"].append(error)

    _trace(
        state,
        node_name,
        "FAILED",
        error=error,
    )

    return state


def request_received(
    state: ReservationState,
) -> ReservationState:
    """
    Register the start of a reservation workflow.
    """
    start_time = _now()
    _ensure_state_collections(state)

    state["reservation_state"] = "REQUEST_RECEIVED"
    state["error"] = None

    state["messages"].append(
        "Reservation request received and entered the workflow."
    )

    _trace(
        state,
        "request_received",
        "COMPLETED",
    )

    logger.info(
        "node_executed",
        node_name="request_received",
        start_time=start_time,
        end_time=_now(),
        reservation_state=state.get("reservation_state"),
    )

    return state


def validate_request(
    state: ReservationState,
) -> ReservationState:
    """
    Validate mandatory reservation data and resolve default providers.
    """
    start_time = _now()
    _ensure_state_collections(state)

    errors: list[str] = []

    if not state.get("customer_id"):
        errors.append("customer_id is required")

    if not state.get("room_id"):
        errors.append("room_id is required")

    if not state.get("check_in"):
        errors.append("check_in is required")

    if not state.get("check_out"):
        errors.append("check_out is required")

    guests = state.get("guests")

    if not isinstance(guests, int) or guests <= 0:
        errors.append("guests must be a positive integer")

    if not errors:
        try:
            date_format = "%Y-%m-%d"

            check_in = datetime.datetime.strptime(
                state["check_in"],
                date_format,
            )

            check_out = datetime.datetime.strptime(
                state["check_out"],
                date_format,
            )

            if check_in >= check_out:
                errors.append(
                    "check_in date must be before check_out date"
                )

        except (TypeError, ValueError):
            errors.append(
                "date format must be YYYY-MM-DD"
            )

    if errors:
        _fail_state(
            state=state,
            node_name="validate_request",
            error=(
                "Request validation failed: "
                + "; ".join(errors)
            ),
        )

    else:
        country = (
            state.get("country")
            or settings.DEFAULT_COUNTRY
        )

        provider = (
            state.get("provider")
            or settings.get_provider_for_country(country)
        )

        currency = (
            state.get("currency")
            or settings.get_currency_for_country(country)
        )

        llm_provider = (
            state.get("llm_provider")
            or settings.DEFAULT_LLM_PROVIDER
        )

        llm_model = (
            state.get("llm_model")
            or settings.DEFAULT_LLM_MODEL
        )

        state["country"] = country
        state["provider"] = provider
        state["currency"] = currency
        state["llm_provider"] = llm_provider
        state["llm_model"] = llm_model
        state["system_prompt"] = SYSTEM_PROMPT

        # The idempotency key is intentionally not generated here.
        # reservation_id may not exist until create_payment_link().
        state["reservation_state"] = "VALIDATED"
        state["error"] = None

        state["messages"].append(
            "Request validated. "
            f"Provider={provider}, "
            f"currency={currency}, "
            f"country={country}, "
            f"llm={llm_provider}."
        )

        _trace(
            state,
            "validate_request",
            "COMPLETED",
            provider=provider,
            currency=currency,
            country=country,
            llm_provider=llm_provider,
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
        llm_provider=state.get("llm_provider"),
    )

    return state


def check_availability(
    state: ReservationState,
) -> ReservationState:
    """
    Check room availability through the controlled MCP Tool layer.
    """
    start_time = _now()
    _ensure_state_collections(state)

    if state.get("reservation_state") == "FAILED":
        return state

    try:
        result = mcp_server.call_tool(
            "check_availability",
            room_id=state["room_id"],
            check_in=state["check_in"],
            check_out=state["check_out"],
        )

        if result.get("status") == "FAILED":
            _fail_state(
                state=state,
                node_name="check_availability",
                error=result.get(
                    "error",
                    "Failed checking availability",
                ),
            )

        elif result.get("available") is True:
            state["reservation_state"] = (
                "AVAILABILITY_CONFIRMED"
            )

            state["messages"].append(
                result.get(
                    "message",
                    "Room is available.",
                )
            )

            _trace(
                state,
                "check_availability",
                "COMPLETED",
            )

        else:
            _fail_state(
                state=state,
                node_name="check_availability",
                error=result.get(
                    "message",
                    "Room is not available.",
                ),
            )

    except Exception as exc:
        _fail_state(
            state=state,
            node_name="check_availability",
            error=(
                "Availability check failed: "
                f"{exc}"
            ),
        )

    logger.info(
        "node_executed",
        node_name="check_availability",
        start_time=start_time,
        end_time=_now(),
        reservation_state=state.get("reservation_state"),
    )

    return state


def calculate_price(
    state: ReservationState,
) -> ReservationState:
    """
    Calculate the reservation price through the MCP Tool layer.
    """
    start_time = _now()
    _ensure_state_collections(state)

    if state.get("reservation_state") == "FAILED":
        return state

    try:
        result = mcp_server.call_tool(
            "calculate_price",
            room_id=state["room_id"],
            check_in=state["check_in"],
            check_out=state["check_out"],
            guests=state["guests"],
        )

        if result.get("status") == "FAILED":
            _fail_state(
                state=state,
                node_name="calculate_price",
                error=result.get(
                    "error",
                    "Failed to calculate price",
                ),
            )

        else:
            total_price = result.get("total_price")

            if total_price is None:
                _fail_state(
                    state=state,
                    node_name="calculate_price",
                    error=(
                        "Price calculation failed: "
                        "total_price was not returned"
                    ),
                )

            else:
                currency = (
                    state.get("currency")
                    or result.get("currency")
                    or settings.DEFAULT_CURRENCY
                )

                state["total_price"] = total_price
                state["currency"] = currency
                state["reservation_state"] = (
                    "PRICE_CALCULATED"
                )

                state["messages"].append(
                    "Price calculated: "
                    f"{currency.upper()} {total_price}."
                )

                _trace(
                    state,
                    "calculate_price",
                    "COMPLETED",
                    total_price=total_price,
                    currency=currency,
                )

    except Exception as exc:
        _fail_state(
            state=state,
            node_name="calculate_price",
            error=(
                "Price calculation failed: "
                f"{exc}"
            ),
        )

    logger.info(
        "node_executed",
        node_name="calculate_price",
        start_time=start_time,
        end_time=_now(),
        reservation_state=state.get("reservation_state"),
        currency=state.get("currency"),
        total_price=state.get("total_price"),
    )

    return state


def retrieve_policy(
    state: ReservationState,
) -> ReservationState:
    """
    Retrieve hotel policy context through the provider-agnostic RAG layer.

    For the MVP, the policy document is indexed in memory during the
    workflow execution. In production, policy documents should be
    indexed separately during ingestion or deployment.
    """
    start_time = _now()
    _ensure_state_collections(state)

    if state.get("reservation_state") == "FAILED":
        return state

    try:
        retriever = create_retriever(
            embedding_provider="mock",
            embedding_model="mock-384",
            vector_store_provider="memory",
        )

        # MVP fixture only.
        # Production documents should already exist in the vector store.
        retriever.index_document(
            document_id="hotel_policy_001",
            text=(
                "Refunds are available up to 24 hours before check-in.\n\n"
                "Cancellation is allowed up to 48 hours before arrival.\n\n"
                "Late cancellation may generate a one-night charge.\n\n"
                "Guests must present official identification at check-in."
            ),
            metadata={
                "source": "workflow_policy",
                "document_type": "hotel_policy",
            },
        )

        context = retriever.retrieve_context(
            query=(
                "What is the refund and cancellation policy "
                "for this hotel reservation?"
            ),
            top_k=2,
        )

        state["reservation_state"] = "POLICY_RETRIEVED"

        if not context or not context.strip():
            state["rag_context"] = ""

            state["messages"].append(
                "No policy context was found. "
                "Continuing without RAG context."
            )

            _trace(
                state,
                "retrieve_policy",
                "NO_CONTEXT",
            )

        else:
            state["rag_context"] = context.strip()

            state["messages"].append(
                "Cancellation and refund policy "
                "retrieved through Local RAG."
            )

            _trace(
                state,
                "retrieve_policy",
                "COMPLETED",
                context_length=len(context),
            )

    except Exception as exc:
        _fail_state(
            state=state,
            node_name="retrieve_policy",
            error=(
                "Failed to retrieve policy context: "
                f"{exc}"
            ),
        )

    logger.info(
        "node_executed",
        node_name="retrieve_policy",
        start_time=start_time,
        end_time=_now(),
        reservation_state=state.get("reservation_state"),
        rag_context_available=bool(
            state.get("rag_context")
        ),
    )

    return state


def generate_llm_summary(
    state: ReservationState,
) -> ReservationState:
    """
    Generate a reservation summary with the provider-agnostic LLM Router.

    The retrieved RAG context is explicitly added to the prompt so that
    policy information can ground the model response.
    """
    start_time = _now()
    _ensure_state_collections(state)

    if state.get("reservation_state") == "FAILED":
        return state

    rag_context = (
        state.get("rag_context")
        or "No hotel policy context was retrieved."
    )

    user_prompt = (
        f"{RESERVATION_STATUS_PROMPT}\n\n"
        "Reservation information:\n"
        f"- Reservation state: {state.get('reservation_state')}\n"
        f"- Customer ID: {state.get('customer_id')}\n"
        f"- Room ID: {state.get('room_id')}\n"
        f"- Check-in: {state.get('check_in')}\n"
        f"- Check-out: {state.get('check_out')}\n"
        f"- Guests: {state.get('guests')}\n"
        f"- Country: {state.get('country')}\n"
        f"- Currency: {state.get('currency')}\n"
        f"- Payment provider: {state.get('provider')}\n"
        f"- Total price: {state.get('total_price')}\n\n"
        "Retrieved hotel policy context:\n"
        f"{rag_context}\n\n"
        "Generate a concise reservation and payment summary. "
        "Use the retrieved policy only when it is relevant. "
        "Do not invent policies, prices, payment confirmations "
        "or reservation confirmations."
    )

    state["user_prompt"] = user_prompt

    try:
        router = LLMRouter(
            provider=state.get("llm_provider"),
            model=state.get("llm_model"),
        )

        response = router.generate(
            prompt=user_prompt,
            system_prompt=(
                state.get("system_prompt")
                or SYSTEM_PROMPT
            ),
            metadata={
                "reservation_id": state.get(
                    "reservation_id"
                ),
                "node": "generate_llm_summary",
                "rag_context_used": bool(
                    state.get("rag_context")
                ),
            },
        )

        state["llm_response"] = response

        state["messages"].append(
            "LLM summary generated using "
            f"{response.get('provider')} / "
            f"{response.get('model')}."
        )

        _trace(
            state,
            "generate_llm_summary",
            "COMPLETED",
            llm_provider=response.get("provider"),
            llm_model=response.get("model"),
            rag_context_used=bool(
                state.get("rag_context")
            ),
        )

    except Exception as exc:
        _fail_state(
            state=state,
            node_name="generate_llm_summary",
            error=(
                "LLM summary generation failed: "
                f"{exc}"
            ),
        )

    logger.info(
        "node_executed",
        node_name="generate_llm_summary",
        start_time=start_time,
        end_time=_now(),
        reservation_state=state.get("reservation_state"),
        llm_provider=state.get("llm_provider"),
        llm_model=state.get("llm_model"),
        rag_context_used=bool(
            state.get("rag_context")
        ),
    )

    return state


def create_payment_link(
    state: ReservationState,
) -> ReservationState:
    """
    Generate a payment link through the controlled MCP Tool layer.

    This node never charges the customer and never confirms payment.
    It only creates a pending payment session.
    """
    start_time = _now()
    _ensure_state_collections(state)

    if state.get("reservation_state") == "FAILED":
        return state

    reservation_id = state.get("reservation_id")

    if not reservation_id:
        reservation_id = (
            f"res_{uuid.uuid4().hex[:8]}"
        )
        state["reservation_id"] = reservation_id

    provider = (
        state.get("provider")
        or settings.PAYMENT_PROVIDER_DEFAULT
    )

    currency = (
        state.get("currency")
        or settings.DEFAULT_CURRENCY
    )

    # Generate only after reservation_id exists.
    idempotency_key = (
        state.get("idempotency_key")
        or f"idem_pay_{provider}_{reservation_id}"
    )

    state["provider"] = provider
    state["currency"] = currency
    state["idempotency_key"] = idempotency_key

    try:
        result = mcp_server.call_tool(
            "create_payment_link",
            reservation_id=reservation_id,
            amount=state["total_price"],
            currency=currency,
            provider=provider,
        )

        if result.get("status") == "FAILED":
            _fail_state(
                state=state,
                node_name="create_payment_link",
                error=result.get(
                    "error",
                    "Failed to create payment link",
                ),
            )

        else:
            payment_link = result.get("payment_link")

            if not payment_link:
                _fail_state(
                    state=state,
                    node_name="create_payment_link",
                    error=(
                        "Payment link generation failed: "
                        "provider returned no payment_link"
                    ),
                )

            else:
                state["payment_link"] = payment_link
                state["payment_id"] = result.get(
                    "payment_id"
                )
                state["payment_session_id"] = result.get(
                    "payment_session_id"
                )

                state["payment_state"] = result.get(
                    "status",
                    "PENDING",
                )

                state["idempotency_key"] = result.get(
                    "idempotency_key",
                    idempotency_key,
                )

                # This is the intended terminal state for Sprint 6A.
                state["reservation_state"] = (
                    "PENDING_PAYMENT"
                )

                state["messages"].append(
                    "Payment link generated using "
                    f"{provider}: {payment_link}"
                )

                _trace(
                    state,
                    "create_payment_link",
                    "COMPLETED",
                    reservation_id=reservation_id,
                    payment_id=state.get("payment_id"),
                    provider=provider,
                    currency=currency,
                    idempotency_key=state.get(
                        "idempotency_key"
                    ),
                )

    except Exception as exc:
        _fail_state(
            state=state,
            node_name="create_payment_link",
            error=(
                "Payment link generation failed: "
                f"{exc}"
            ),
        )

    logger.info(
        "node_executed",
        node_name="create_payment_link",
        start_time=start_time,
        end_time=_now(),
        reservation_state=state.get(
            "reservation_state"
        ),
        provider=state.get("provider"),
        currency=state.get("currency"),
        reservation_id=state.get(
            "reservation_id"
        ),
        payment_id=state.get("payment_id"),
        idempotency_key=state.get(
            "idempotency_key"
        ),
    )

    return state


def finish(
    state: ReservationState,
) -> ReservationState:
    """
    Finish Sprint 6A after generating a pending payment link.
    """
    start_time = _now()
    _ensure_state_collections(state)

    if state.get("reservation_state") == "PENDING_PAYMENT":
        state["messages"].append(
            "Workflow finished with payment pending. "
            "Reservation confirmation requires an external "
            "payment webhook."
        )

        _trace(
            state,
            "finish",
            "COMPLETED",
            final_state="PENDING_PAYMENT",
        )

    else:
        state["messages"].append(
            "Workflow finished."
        )

        _trace(
            state,
            "finish",
            "COMPLETED",
            final_state=state.get(
                "reservation_state"
            ),
        )

    logger.info(
        "node_executed",
        node_name="finish",
        start_time=start_time,
        end_time=_now(),
        reservation_state=state.get(
            "reservation_state"
        ),
        provider=state.get("provider"),
        currency=state.get("currency"),
        country=state.get("country"),
        llm_provider=state.get(
            "llm_provider"
        ),
    )

    return state


# ------------------------------------------------------------------
# Routing
# ------------------------------------------------------------------


def _route_or_end(
    state: ReservationState,
    next_node: str,
) -> str:
    """
    Route to END when the workflow is failed; otherwise continue.
    """
    if state.get("reservation_state") == "FAILED":
        return END

    return next_node


def route_request_received(
    state: ReservationState,
) -> str:
    return _route_or_end(
        state,
        "validate_request",
    )


def route_validation(
    state: ReservationState,
) -> str:
    return _route_or_end(
        state,
        "check_availability",
    )


def route_availability(
    state: ReservationState,
) -> str:
    return _route_or_end(
        state,
        "calculate_price",
    )


def route_price(
    state: ReservationState,
) -> str:
    return _route_or_end(
        state,
        "retrieve_policy",
    )


def route_retrieve_policy(
    state: ReservationState,
) -> str:
    return _route_or_end(
        state,
        "generate_llm_summary",
    )


def route_llm_summary(
    state: ReservationState,
) -> str:
    return _route_or_end(
        state,
        "create_payment_link",
    )


def route_payment_link(
    state: ReservationState,
) -> str:
    return _route_or_end(
        state,
        "finish",
    )


# ------------------------------------------------------------------
# StateGraph
# ------------------------------------------------------------------

workflow = StateGraph(ReservationState)

workflow.add_node(
    "request_received",
    request_received,
)

workflow.add_node(
    "validate_request",
    validate_request,
)

workflow.add_node(
    "check_availability",
    check_availability,
)

workflow.add_node(
    "calculate_price",
    calculate_price,
)

workflow.add_node(
    "retrieve_policy",
    retrieve_policy,
)

workflow.add_node(
    "generate_llm_summary",
    generate_llm_summary,
)

workflow.add_node(
    "create_payment_link",
    create_payment_link,
)

workflow.add_node(
    "finish",
    finish,
)

workflow.set_entry_point(
    "request_received"
)

workflow.add_conditional_edges(
    "request_received",
    route_request_received,
)

workflow.add_conditional_edges(
    "validate_request",
    route_validation,
)

workflow.add_conditional_edges(
    "check_availability",
    route_availability,
)

workflow.add_conditional_edges(
    "calculate_price",
    route_price,
)

workflow.add_conditional_edges(
    "retrieve_policy",
    route_retrieve_policy,
)

workflow.add_conditional_edges(
    "generate_llm_summary",
    route_llm_summary,
)

workflow.add_conditional_edges(
    "create_payment_link",
    route_payment_link,
)

workflow.add_edge(
    "finish",
    END,
)

app_graph = workflow.compile()


# ------------------------------------------------------------------
# Local demonstration only
# ------------------------------------------------------------------

if __name__ == "__main__":
    # Local fixture only.
    #
    # This repository access is intentionally outside every LangGraph
    # node. Production code must preserve:
    #
    # LangGraph -> MCP Tool -> Service -> Repository
    #
    # Remove this block when the upstream reservation-creation tool
    # is included in the end-to-end workflow.

    from repositories.reservation_repository import (
        ReservationRepository,
    )

    test_reservation_id = "res_test_123"

    existing_reservation = (
        ReservationRepository.get_reservation(
            test_reservation_id
        )
    )

    if not existing_reservation:
        ReservationRepository.create_reservation(
            {
                "reservation_id": (
                    test_reservation_id
                ),
                "customer_id": "cust_001",
                "room_id": "deluxe-suite",
                "check_in": "2026-07-10",
                "check_out": "2026-07-15",
                "guests": 2,
                "reservation_state": "VALIDATED",
                "created_at": _now(),
                "updated_at": _now(),
            }
        )

    test_state: ReservationState = {
        "reservation_id": test_reservation_id,
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
        "llm_provider": "gemini",
        "llm_model": None,
        "llm_response": None,
        "system_prompt": None,
        "user_prompt": None,
        "policy_context": None,
        "rag_context": None,
        "selected_agent": None,
        "messages": [],
        "execution_trace": [],
        "error": None,
    }

    print(
        "Invoking LangGraph Sprint 6A workflow..."
    )

    final_state = app_graph.invoke(
        test_state
    )

    print("\n--- FINAL STATE ---")
    print(
        json.dumps(
            final_state,
            indent=2,
            default=str,
        )
    )
    print("-------------------")