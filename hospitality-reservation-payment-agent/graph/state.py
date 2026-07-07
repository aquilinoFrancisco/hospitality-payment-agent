# graph/state.py
"""
LangGraph reservation workflow state.

This state is the shared memory of the reservation workflow.

It carries:
- reservation data
- payment configuration
- selected provider
- currency
- workflow messages
- errors

LangGraph nodes should update this state, not access repositories directly.
"""

from __future__ import annotations

from typing import List, Optional, TypedDict


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

    # Pricing
    total_price: Optional[float]

    # RAG / policy context
    policy_context: Optional[List[dict]]

    # Observability
    messages: List[str]
    error: Optional[str]