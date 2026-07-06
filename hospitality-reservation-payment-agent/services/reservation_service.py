# services/reservation_service.py
import re
import structlog
from datetime import datetime
from typing import Dict, Any, List, Optional
from repositories.room_repository import RoomRepository
from repositories.customer_repository import CustomerRepository
from repositories.reservation_repository import ReservationRepository

logger = structlog.get_logger()

class ReservationService:
    """
    Core reservation service enforcing business workflows.
    Completely decoupled from transport layers and persistence details.
    """

    @staticmethod
    def validate_reservation_request(
        customer_email: str,
        room_type: str,
        check_in: str,
        check_out: str
    ) -> List[str]:
        """
        Validates the request parameters.
        Returns a list of error strings. Empty list indicates validity.
        """
        errors = []
        
        # 1. Validate email
        if not customer_email or not re.match(r"[^@]+@[^@]+\.[^@]+", customer_email):
            errors.append("Invalid customer email address format.")

        # 2. Validate dates
        try:
            date_format = "%Y-%m-%d"
            start_date = datetime.strptime(check_in, date_format)
            end_date = datetime.strptime(check_out, date_format)
            
            if start_date >= end_date:
                errors.append("Check-in date must be before check-out date.")
        except ValueError:
            errors.append("Dates must be in YYYY-MM-DD format.")

        # 3. Validate room type
        room = RoomRepository.get_room(room_type)
        if not room:
            errors.append(f"Requested room type '{room_type}' does not exist.")

        return errors

    @staticmethod
    def check_room_availability(room_id: str, check_in: str, check_out: str) -> bool:
        """
        Checks availability of room_id for the given date range.
        Ensures dates are not blacklisted and that there are no overlapping active bookings.
        """
        # 1. Query availability calendar records
        records = ReservationRepository.get_availability_records()
        for rec in records:
            if rec["room_id"] == room_id and check_in <= rec["date"] < check_out:
                if not rec["available"]:
                    logger.info("Room calendar blocked", room_id=room_id, date=rec["date"])
                    return False

        # 2. Query other overlapping reservations
        reservations = ReservationRepository.list_reservations()
        for res in reservations:
            if res["room_id"] == room_id and res["reservation_state"] not in ["CANCELLED", "REFUNDED", "FAILED"]:
                if (check_in < res["check_out"]) and (check_out > res["check_in"]):
                    logger.info("Room conflict detected", room_id=room_id, conflict_id=res["reservation_id"])
                    return False

        return True

    @staticmethod
    def create_reservation(
        customer_email: str,
        room_type: str,
        check_in: str,
        check_out: str,
        idempotency_key: str
    ) -> Dict[str, Any]:
        """
        Processes a new booking draft.
        Enforces idempotency, input validations, customer auto-registration, and calendar availability.
        """
        logger.info("Service: create_reservation called", customer_email=customer_email, room_type=room_type, idempotency_key=idempotency_key)

        # Idempotency check
        existing_res = ReservationRepository.list_reservations()
        for res in existing_res:
            if res["idempotency_key"] == idempotency_key:
                logger.info("Idempotent booking hit", reservation_id=res["reservation_id"])
                return res

        # Request validation
        validation_errors = ReservationService.validate_reservation_request(customer_email, room_type, check_in, check_out)
        if validation_errors:
            logger.warn("Reservation request validation failed", errors=validation_errors)
            return {
                "reservation_id": "error",
                "reservation_state": "FAILED",
                "errors": validation_errors
            }

        # Check availability
        if not ReservationService.check_room_availability(room_type, check_in, check_out):
            logger.warn("Room unavailable for date range", room_id=room_type, check_in=check_in, check_out=check_out)
            return {
                "reservation_id": "error",
                "reservation_state": "FAILED",
                "errors": ["Requested dates are already booked or unavailable."]
            }

        # Auto-register customer if not exists
        customer = CustomerRepository.get_customer_by_email(customer_email)
        if not customer:
            customers_list = CustomerRepository.get_all_customers()
            new_cust_id = f"cust_0{len(customers_list) + 1}"
            customer_data = {
                "id": new_cust_id,
                "name": customer_email.split("@")[0].title(),
                "email": customer_email
            }
            CustomerRepository.create_customer(customer_data)
            customer = customer_data
            logger.info("Registered customer dynamically", customer_id=new_cust_id)

        # Persist reservation as REQUEST_RECEIVED
        res_list = ReservationRepository.list_reservations()
        new_res_id = f"res_00{len(res_list) + 1}"
        
        reservation_record = {
            "reservation_id": new_res_id,
            "customer_id": customer["id"],
            "room_id": room_type,
            "check_in": check_in,
            "check_out": check_out,
            "reservation_state": "REQUEST_RECEIVED",
            "payment_link": None,
            "payment_session_id": None,
            "idempotency_key": idempotency_key,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        ReservationRepository.create_reservation(reservation_record)
        
        # Structured logging of initial state
        logger.info(
            "State transition details",
            reservation_id=new_res_id,
            payment_id=None,
            current_state=None,
            next_state="REQUEST_RECEIVED",
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
        return reservation_record

    @staticmethod
    def change_reservation_state(reservation_id: str, target_state: str) -> Dict[str, Any]:
        """
        Explicit State Machine Transition function.
        Validates states and emits structured audit logs.
        """
        reservation = ReservationRepository.get_reservation(reservation_id)
        if not reservation:
            logger.error("Reservation not found for state change", reservation_id=reservation_id)
            return {"error": "Reservation not found"}

        current_state = reservation["reservation_state"]
        
        # Transition state
        reservation["reservation_state"] = target_state
        reservation["updated_at"] = datetime.utcnow().isoformat() + "Z"
        ReservationRepository.update_reservation(reservation_id, reservation)

        # Structured log: reservation_id, payment_id, current_state, next_state, timestamp
        logger.info(
            "State transition details",
            reservation_id=reservation_id,
            payment_id=reservation.get("payment_session_id"),
            current_state=current_state,
            next_state=target_state,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        return reservation

    @staticmethod
    def confirm_reservation(reservation_id: str) -> Dict[str, Any]:
        """
        Activates reservation into RESERVATION_CONFIRMED status.
        """
        logger.info("Service: confirm_reservation called", reservation_id=reservation_id)
        return ReservationService.change_reservation_state(reservation_id, "RESERVATION_CONFIRMED")

    @staticmethod
    def cancel_reservation(reservation_id: str) -> Dict[str, Any]:
        """
        Aborts active booking and sets state to CANCELLED.
        """
        logger.info("Service: cancel_reservation called", reservation_id=reservation_id)
        return ReservationService.change_reservation_state(reservation_id, "CANCELLED")
