# tests/test_business_logic.py
import os
import unittest
from services.reservation_service import ReservationService
from services.payment_service import PaymentService
from repositories.room_repository import RoomRepository
from repositories.customer_repository import CustomerRepository
from repositories.reservation_repository import ReservationRepository
from repositories.payment_repository import PaymentRepository

class TestBusinessLogic(unittest.TestCase):
    """
    Unit testing suite verifying Phase 3 MVP business logic and repositories layer.
    """

    def test_room_repository(self):
        # 1. Fetch all rooms
        rooms = RoomRepository.get_all_rooms()
        self.assertGreaterEqual(len(rooms), 1)

        # 2. Fetch specific room
        first_room_id = rooms[0]["id"]
        room = RoomRepository.get_room(first_room_id)
        self.assertIsNotNone(room)
        self.assertEqual(room["id"], first_room_id)

    def test_customer_repository(self):
        # 1. Fetch all customers
        customers = CustomerRepository.get_all_customers()
        self.assertGreaterEqual(len(customers), 1)

        # 2. Fetch customer by email (case insensitive)
        first_cust = customers[0]
        fetched = CustomerRepository.get_customer_by_email(first_cust["email"])
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["id"], first_cust["id"])

    def test_validation_logic(self):
        # Validate bad email format
        errors = ReservationService.validate_reservation_request(
            customer_email="not-an-email",
            room_type="deluxe-suite",
            check_in="2026-07-10",
            check_out="2026-07-15"
        )
        self.assertTrue(any("email" in err.lower() for err in errors))

        # Validate invalid room type
        errors = ReservationService.validate_reservation_request(
            customer_email="guest@test.com",
            room_type="non-existent-room-type",
            check_in="2026-07-10",
            check_out="2026-07-15"
        )
        self.assertTrue(any("room type" in err.lower() or "does not exist" in err.lower() for err in errors))

        # Validate chronological check-out before check-in
        errors = ReservationService.validate_reservation_request(
            customer_email="guest@test.com",
            room_type="deluxe-suite",
            check_in="2026-07-15",
            check_out="2026-07-10"
        )
        self.assertTrue(any("before" in err.lower() or "after" in err.lower() for err in errors))

    def test_price_calculation(self):
        rooms = RoomRepository.get_all_rooms()
        if rooms:
            room = rooms[0]
            # Calculate price for 5 nights
            calculated = PaymentService.calculate_price(room["id"], "2026-07-10", "2026-07-15")
            expected = room["base_price"] * 5
            self.assertEqual(calculated, expected)

    def test_idempotent_reservation_flow(self):
        # Create a booking with a unique idempotency key
        idem_key = "test_unique_idem_key_999"
        
        # Ensure we clean up any pre-existing test record first
        all_res = ReservationRepository.list_reservations()
        for res in all_res:
            if res["idempotency_key"] == idem_key:
                # Mock deletion by removing from list (since repo has simple append, we just skip check in real use)
                pass

        booking = ReservationService.create_reservation(
            customer_email="test.suite@example.com",
            room_type="deluxe-suite",
            check_in="2026-12-01",
            check_out="2026-12-05",
            idempotency_key=idem_key
        )
        self.assertIsNotNone(booking)
        self.assertEqual(booking["reservation_state"], "REQUEST_RECEIVED")
        self.assertEqual(booking["idempotency_key"], idem_key)

        # Trigger second creation with same key to verify idempotency check
        duplicate_booking = ReservationService.create_reservation(
            customer_email="test.suite@example.com",
            room_type="deluxe-suite",
            check_in="2026-12-01",
            check_out="2026-12-05",
            idempotency_key=idem_key
        )
        self.assertEqual(duplicate_booking["reservation_id"], booking["reservation_id"])

if __name__ == "__main__":
    unittest.main()
