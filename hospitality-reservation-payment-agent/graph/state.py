# graph/state.py
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
    error: Optional[str]

