# services/payment_service.py
import structlog
from datetime import datetime
from typing import Dict, Any, List, Optional
from repositories.room_repository import RoomRepository
from repositories.reservation_repository import ReservationRepository
from repositories.payment_repository import PaymentRepository
from services.reservation_service import ReservationService

logger = structlog.get_logger()

class PaymentService:
    """
    Core payment business service coordinating mock Stripe operations.
    Strictly decoupled from actual payment gateway client SDKs.
    """

    @staticmethod
    def calculate_price(room_id: str, check_in: str, check_out: str) -> float:
        """
        Calculates the pricing based on room base_price and duration in nights.
        """
        logger.info("Service: calculate_price called", room_id=room_id, check_in=check_in, check_out=check_out)
        room = RoomRepository.get_room(room_id)
        if not room:
            raise ValueError(f"Room type '{room_id}' not found.")

        try:
            date_format = "%Y-%m-%d"
            start_date = datetime.strptime(check_in, date_format)
            end_date = datetime.strptime(check_out, date_format)
            delta = end_date - start_date
            nights = max(1, delta.days)
        except Exception as e:
            logger.warn("Invalid date formatting. Defaulting billing calculation to 1 night.", error=str(e))
            nights = 1

        total_price = room["base_price"] * nights
        logger.info("Calculated pricing", room_id=room_id, base_price=room["base_price"], nights=nights, total_price=total_price)
        return total_price

    @staticmethod
    def create_payment_link(reservation_id: str, amount: float, idempotency_key: str) -> Dict[str, Any]:
        """
        Generates a fake payment session and registers a PENDING payment.
        Transitions the reservation to 'PENDING_PAYMENT' state.
        """
        logger.info("Service: create_payment_link called", reservation_id=reservation_id, amount=amount, idempotency_key=idempotency_key)
        
        target_res = ReservationRepository.get_reservation(reservation_id)
        if not target_res:
            raise ValueError(f"Reservation '{reservation_id}' not found.")

        # Check existing payment for idempotency
        payments = PaymentRepository.list_payments()
        for pay in payments:
            if pay["reservation_id"] == reservation_id and pay["status"] == "PENDING":
                logger.info("Pending payment session already exists", payment_id=pay["payment_id"])
                return {
                    "payment_id": pay["payment_id"],
                    "payment_link": pay["payment_link"],
                    "payment_session_id": pay["payment_session_id"],
                    "status": pay["status"]
                }

        # Mock Stripe payment details
        mock_sess_id = f"demo-session-00{len(payments) + 1}"
        mock_pay_id = f"pay_00{len(payments) + 1}"
        fake_payment_link = f"https://sandbox.stripe.com/pay/demo-payment-00{len(payments) + 1}"

        # Register transaction log via repository
        new_payment = {
            "payment_id": mock_pay_id,
            "reservation_id": reservation_id,
            "amount": amount,
            "currency": "usd",
            "status": "PENDING",
            "payment_session_id": mock_sess_id,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        PaymentRepository.create_payment(new_payment)

        # Update reservation details in repository and change state
        target_res["payment_link"] = fake_payment_link
        target_res["payment_session_id"] = mock_sess_id
        target_res["updated_at"] = datetime.utcnow().isoformat() + "Z"
        ReservationRepository.update_reservation(reservation_id, target_res)

        # Transition the reservation to PENDING_PAYMENT state
        ReservationService.change_reservation_state(reservation_id, "PENDING_PAYMENT")

        logger.info("Created payment checkout session link", payment_id=mock_pay_id, payment_link=fake_payment_link)
        
        # Structured log requirement
        logger.info(
            "State transition details",
            reservation_id=reservation_id,
            payment_id=mock_pay_id,
            current_state="PRICE_CALCULATED",
            next_state="PENDING_PAYMENT",
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

        return {
            "payment_id": mock_pay_id,
            "payment_link": fake_payment_link,
            "payment_session_id": mock_sess_id,
            "status": "PENDING"
        }

    @staticmethod
    def get_payment_status(payment_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the payment status from storage.
        """
        logger.info("Service: get_payment_status called", payment_id=payment_id)
        return PaymentRepository.get_payment(payment_id)

    @staticmethod
    def mark_payment_completed(payment_session_id: str) -> Dict[str, Any]:
        """
        Simulates callback verification when Stripe Sandbox succeeds.
        Transitions state: PENDING_PAYMENT -> PAID -> RESERVATION_CONFIRMED
        """
        logger.info("Service: mark_payment_completed invoked", payment_session_id=payment_session_id)
        
        target_payment = PaymentRepository.get_payment_by_session_id(payment_session_id)
        if not target_payment:
            raise ValueError(f"Payment session with id '{payment_session_id}' not found.")
        
        # Update Payment transaction record to COMPLETED
        target_payment["status"] = "COMPLETED"
        target_payment["updated_at"] = datetime.utcnow().isoformat() + "Z"
        PaymentRepository.update_payment(target_payment["payment_id"], target_payment)

        reservation_id = target_payment["reservation_id"]
        
        # Sequentially transition states
        ReservationService.change_reservation_state(reservation_id, "PAID")
        ReservationService.change_reservation_state(reservation_id, "RESERVATION_CONFIRMED")

        logger.info("Payment captured. Reservation confirmed active", reservation_id=reservation_id)
        return {
            "payment_id": target_payment["payment_id"],
            "reservation_id": reservation_id,
            "status": "COMPLETED",
            "updated_at": target_payment["updated_at"]
        }

    @staticmethod
    def issue_refund(payment_session_id: str, amount: float) -> Dict[str, Any]:
        """
        Performs refund transaction cancellation.
        Transitions reservation state to REFUNDED.
        """
        logger.info("Service: issue_refund called", payment_session_id=payment_session_id, amount=amount)
        
        target_payment = PaymentRepository.get_payment_by_session_id(payment_session_id)
        if not target_payment:
            raise ValueError(f"Completed payment session '{payment_session_id}' not found.")

        # Update payment transaction record to REFUNDED
        target_payment["status"] = "REFUNDED"
        target_payment["updated_at"] = datetime.utcnow().isoformat() + "Z"
        PaymentRepository.update_payment(target_payment["payment_id"], target_payment)

        # Transition reservation state to REFUNDED
        reservation_id = target_payment["reservation_id"]
        ReservationService.change_reservation_state(reservation_id, "REFUNDED")

        return {
            "payment_id": target_payment["payment_id"],
            "reservation_id": reservation_id,
            "amount_refunded": amount,
            "status": "REFUNDED"
        }
