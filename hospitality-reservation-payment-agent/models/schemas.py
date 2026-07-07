# models/schemas.py
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ReservationState(str, Enum):
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
    id: str = Field(..., example="deluxe-suite")
    name: str = Field(..., example="Deluxe Suite")
    base_price: float = Field(..., example=250.00)
    capacity: int = Field(..., example=3)


class Customer(BaseModel):
    id: str = Field(..., example="cust_01")
    name: str = Field(..., example="Aquilino Francisco")
    email: str = Field(..., example="aquilino.francisco@gmail.com")


class Reservation(BaseModel):
    reservation_id: str = Field(..., example="res_mock_8f21bc")
    customer_id: str = Field(..., example="cust_01")
    room_id: str = Field(..., example="deluxe-suite")

    country: str = Field("MX", example="MX")
    provider: str = Field("stripe", example="conekta")
    currency: str = Field("mxn", example="mxn")

    reservation_state: ReservationState = Field(
        ...,
        example=ReservationState.REQUEST_RECEIVED,
    )

    payment_link: Optional[str] = Field(
        None,
        example="https://sandbox.conekta.local/pay/conekta_order_res_001",
    )
    payment_id: Optional[str] = Field(None, example="pay_001")
    payment_session_id: Optional[str] = Field(None, example="sess_mock_8f21bc")
    idempotency_key: str = Field(..., example="idem_pay_conekta_res_001")

    created_at: str = Field(..., example="2026-07-06T12:00:00Z")
    updated_at: str = Field(..., example="2026-07-06T12:00:00Z")


class Payment(BaseModel):
    payment_id: str = Field(..., example="pay_001")
    reservation_id: str = Field(..., example="res_001")

    provider: str = Field("stripe", example="mercado_pago")
    amount: float = Field(..., example=1250.0)
    currency: str = Field("usd", example="mxn")

    status: str = Field(..., example="COMPLETED")
    payment_link: Optional[str] = Field(
        None,
        example="https://sandbox.mercadopago.local/checkout/mp_preference_res_001",
    )
    payment_session_id: Optional[str] = Field(None, example="sess_001")
    idempotency_key: str = Field(..., example="idem_pay_mercado_pago_res_001")

    created_at: str = Field(..., example="2026-07-06T10:04:00Z")
    updated_at: str = Field(..., example="2026-07-06T10:05:00Z")


class ReservationRequest(BaseModel):
    customer_id: str = Field(..., example="cust_01")
    room_id: str = Field(..., example="deluxe-suite")
    check_in: str = Field(..., example="2026-07-10")
    check_out: str = Field(..., example="2026-07-15")
    guests: int = Field(2, example=2)

    country: str = Field("MX", example="MX")
    provider: Optional[str] = Field(
        None,
        example="conekta",
        description="stripe, conekta, mercado_pago. If omitted, backend selects default.",
    )
    currency: Optional[str] = Field(
        None,
        example="mxn",
        description="mxn, usd, eur, etc. If omitted, backend selects default by country.",
    )

    idempotency_key: Optional[str] = Field(
        None,
        example="idem_pay_conekta_res_001",
    )


class ReservationResponse(BaseModel):
    reservation_id: str = Field(..., example="res_mock_8f21bc")
    status: ReservationState = Field(..., example=ReservationState.PENDING_PAYMENT)

    country: str = Field("MX", example="MX")
    provider: str = Field("stripe", example="conekta")
    currency: str = Field("mxn", example="mxn")

    payment_id: Optional[str] = Field(None, example="pay_001")
    payment_session_id: Optional[str] = Field(None, example="sess_mock_8f21bc")
    payment_link: Optional[str] = Field(
        None,
        example="https://sandbox.conekta.local/pay/conekta_order_res_001",
    )
    idempotency_key: Optional[str] = Field(
        None,
        example="idem_pay_conekta_res_001",
    )

    total_price: float = Field(..., example=1250.0)


class PaymentResponse(BaseModel):
    payment_id: str = Field(..., example="pay_001")
    reservation_id: str = Field(..., example="res_001")

    provider: str = Field("stripe", example="mercado_pago")
    amount: float = Field(..., example=1250.0)
    currency: str = Field("usd", example="mxn")
    status: str = Field(..., example="COMPLETED")

    payment_link: Optional[str] = Field(
        None,
        example="https://sandbox.mercadopago.local/checkout/mp_preference_res_001",
    )
    payment_session_id: Optional[str] = Field(None, example="sess_001")
    idempotency_key: Optional[str] = Field(
        None,
        example="idem_pay_mercado_pago_res_001",
    )


class ReservationStatus(BaseModel):
    reservation_id: str = Field(..., example="res_mock_8f21bc")
    status: ReservationState = Field(..., example=ReservationState.RESERVATION_CONFIRMED)

    country: Optional[str] = Field(None, example="MX")
    provider: Optional[str] = Field(None, example="conekta")
    currency: Optional[str] = Field(None, example="mxn")

    payment_id: Optional[str] = Field(None, example="pay_001")
    payment_session_id: Optional[str] = Field(None, example="sess_mock_8f21bc")
    idempotency_key: Optional[str] = Field(None, example="idem_pay_conekta_res_001")

    updated_at: str = Field(..., example="2026-07-06T12:05:00Z")
    errors: List[str] = Field(default_factory=list, example=[])