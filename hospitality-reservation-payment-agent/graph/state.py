# graph/state.py
"""
LangGraph reservation workflow state.

This state is the shared memory of the reservation workflow.

It carries:
- reservation data
- payment configuration
- LLM configuration
- selected providers
- currency
- RAG / policy context
- workflow messages
- execution trace
- errors

LangGraph nodes should update this state, not access repositories directly.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class ReservationState(TypedDict):
    """
    Shared state for the hospitality reservation workflow.
    """

    # Reservation identity
    reservation_id: Optional[str]
    customer_id: Optional[str]
    room_id: Optional[str]

    # Stay details
    check_in: Optional[str]
    check_out: Optional[str]
    guests: Optional[int]
    country: Optional[str]

    # Workflow states
    reservation_state: Optional[str]
    payment_state: Optional[str]

    # Payment configuration
    provider: Optional[str]
    currency: Optional[str]
    payment_link: Optional[str]
    payment_id: Optional[str]
    payment_session_id: Optional[str]
    idempotency_key: Optional[str]

    # LLM configuration
    llm_provider: Optional[str]
    llm_model: Optional[str]
    llm_response: Optional[Dict[str, Any]]

    # Prompt context
    system_prompt: Optional[str]
    user_prompt: Optional[str]

    # Pricing
    total_price: Optional[float]

    # RAG / policy context
    policy_context: Optional[List[dict]]
    rag_context: Optional[str]

    # Agent routing
    selected_agent: Optional[str]

    # Observability
    messages: List[str]
    execution_trace: List[Dict[str, Any]]
    error: Optional[str]