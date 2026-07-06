# app/api/routes.py
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
    }
