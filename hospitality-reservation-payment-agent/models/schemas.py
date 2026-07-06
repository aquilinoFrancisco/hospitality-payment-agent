# models/schemas.py
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
    status: str = Field(..., example="COMPLETED")  # e.g. PENDING, COMPLETED, FAILED, REFUNDED
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
    errors: List[str] = Field(default_factory=list, example=[])
