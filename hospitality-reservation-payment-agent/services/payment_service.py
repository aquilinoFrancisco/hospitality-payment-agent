# services/payment_service.py
"""
Payment business service.

This service coordinates payment-related business rules using mock JSON
repositories and a Stripe Sandbox client wrapper.

Important:
- The AI agent never charges directly.
- The system only creates payment links.
- Stripe webhook confirmation is the source of truth.
- Every payment operation should be traceable and idempotent.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

import structlog

from integrations.stripe.client import StripeSandboxClient
from repositories.payment_repository import PaymentRepository
from repositories.reservation_repository import ReservationRepository
from repositories.room_repository import RoomRepository
from services.reservation_service import ReservationService

logger = structlog.get_logger()


class PaymentService:
    """
    Core payment business service.

    Coordinates pricing, payment-link creation, payment completion and refunds.
    """

    @staticmethod
    def calculate_price(
        room_id: str,
        check_in: str,
        check_out: str,
    ) -> float:
        """
        Calculate reservation price based on room base price and nights.
        """
        logger.info(
            "payment_calculate_price_called",
            room_id=room_id,
            check_in=check_in,
            check_out=check_out,
        )

        room = RoomRepository.get_room(room_id)

        if not room:
            raise ValueError(f"Room type '{room_id}' not found.")

        try:
            date_format = "%Y-%m-%d"
            start_date = datetime.strptime(check_in, date_format)
            end_date = datetime.strptime(check_out, date_format)
            nights = max(1, (end_date - start_date).days)

        except Exception as exc:
            logger.warning(
                "invalid_date_format_defaulting_to_one_night",
                error=str(exc),
            )
            nights = 1

        total_price = float(room["base_price"]) * nights

        logger.info(
            "payment_price_calculated",
            room_id=room_id,
            base_price=room["base_price"],
            nights=nights,
            total_price=total_price,
        )

        return total_price

    @staticmethod
    def create_payment_link(
        reservation_id: str,
        amount: float,
        currency: str = "usd",
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a safe Stripe Sandbox payment link.

        The payment link is created in mock sandbox mode.

        Args:
            reservation_id: Reservation identifier.
            amount: Amount to charge.
            currency: Payment currency.
            idempotency_key: Unique operation key.

        Returns:
            JSON-safe payment payload.
        """
        idempotency_key = (
            idempotency_key
            or f"idem_pay_{reservation_id}"
        )

        currency = currency.lower()

        logger.info(
            "payment_create_link_called",
            reservation_id=reservation_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        target_reservation = ReservationRepository.get_reservation(
            reservation_id
        )

        if not target_reservation:
            raise ValueError(
                f"Reservation '{reservation_id}' not found."
            )

        payments = PaymentRepository.list_payments()

        for payment in payments:
            if (
                payment.get("reservation_id") == reservation_id
                and payment.get("status") == "PENDING"
            ):
                logger.info(
                    "pending_payment_already_exists",
                    payment_id=payment["payment_id"],
                    reservation_id=reservation_id,
                )

                return {
                    "payment_id": payment["payment_id"],
                    "reservation_id": reservation_id,
                    "payment_link": payment["payment_link"],
                    "payment_session_id": payment["payment_session_id"],
                    "amount": payment.get("amount", amount),
                    "currency": payment.get("currency", currency),
                    "status": payment["status"],
                    "idempotency_key": payment.get(
                        "idempotency_key",
                        idempotency_key,
                    ),
                }

        stripe_client = StripeSandboxClient()

        checkout_session = stripe_client.create_checkout_session(
            reservation_id=reservation_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        payment_id = f"pay_{len(payments) + 1:03d}"
        payment_session_id = checkout_session["id"]
        payment_link = checkout_session["url"]

        now = datetime.utcnow().isoformat() + "Z"

        new_payment = {
            "payment_id": payment_id,
            "reservation_id": reservation_id,
            "amount": amount,
            "currency": currency,
            "status": "PENDING",
            "payment_link": payment_link,
            "payment_session_id": payment_session_id,
            "idempotency_key": idempotency_key,
            "provider": "stripe_sandbox",
            "created_at": now,
            "updated_at": now,
        }

        PaymentRepository.create_payment(new_payment)

        target_reservation["payment_link"] = payment_link
        target_reservation["payment_session_id"] = payment_session_id
        target_reservation["updated_at"] = now

        ReservationRepository.update_reservation(
            reservation_id,
            target_reservation,
        )

        ReservationService.change_reservation_state(
            reservation_id,
            "PENDING_PAYMENT",
        )

        logger.info(
            "payment_link_created",
            reservation_id=reservation_id,
            payment_id=payment_id,
            payment_session_id=payment_session_id,
            current_state="PRICE_CALCULATED",
            next_state="PENDING_PAYMENT",
            currency=currency,
            timestamp=now,
        )

        return {
            "payment_id": payment_id,
            "reservation_id": reservation_id,
            "payment_link": payment_link,
            "payment_session_id": payment_session_id,
            "amount": amount,
            "currency": currency,
            "status": "PENDING",
            "idempotency_key": idempotency_key,
        }

    @staticmethod
    def get_payment_status(
        payment_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve payment status from mock storage.
        """
        logger.info(
            "payment_status_requested",
            payment_id=payment_id,
        )

        return PaymentRepository.get_payment(payment_id)

    @staticmethod
    def mark_payment_completed(
        payment_session_id: str,
    ) -> Dict[str, Any]:
        """
        Simulate Stripe webhook confirmation.

        State transition:
            PENDING_PAYMENT -> PAID -> RESERVATION_CONFIRMED
        """
        logger.info(
            "payment_mark_completed_called",
            payment_session_id=payment_session_id,
        )

        target_payment = PaymentRepository.get_payment_by_session_id(
            payment_session_id
        )

        if not target_payment:
            raise ValueError(
                f"Payment session '{payment_session_id}' not found."
            )

        now = datetime.utcnow().isoformat() + "Z"

        target_payment["status"] = "COMPLETED"
        target_payment["updated_at"] = now

        PaymentRepository.update_payment(
            target_payment["payment_id"],
            target_payment,
        )

        reservation_id = target_payment["reservation_id"]

        ReservationService.change_reservation_state(
            reservation_id,
            "PAID",
        )

        ReservationService.change_reservation_state(
            reservation_id,
            "RESERVATION_CONFIRMED",
        )

        logger.info(
            "payment_completed_reservation_confirmed",
            reservation_id=reservation_id,
            payment_id=target_payment["payment_id"],
            payment_session_id=payment_session_id,
            timestamp=now,
        )

        return {
            "payment_id": target_payment["payment_id"],
            "reservation_id": reservation_id,
            "status": "COMPLETED",
            "currency": target_payment.get("currency", "usd"),
            "updated_at": now,
        }

    @staticmethod
    def issue_refund(
        payment_session_id: str,
        amount: float,
        currency: str = "usd",
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Issue a mock refund and transition reservation to REFUNDED.
        """
        idempotency_key = (
            idempotency_key
            or f"idem_refund_{payment_session_id}"
        )

        currency = currency.lower()

        logger.info(
            "payment_issue_refund_called",
            payment_session_id=payment_session_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        target_payment = PaymentRepository.get_payment_by_session_id(
            payment_session_id
        )

        if not target_payment:
            raise ValueError(
                f"Payment session '{payment_session_id}' not found."
            )

        stripe_client = StripeSandboxClient()

        refund = stripe_client.refund_payment(
            charge_id=target_payment["payment_id"],
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        now = datetime.utcnow().isoformat() + "Z"

        target_payment["status"] = "REFUNDED"
        target_payment["updated_at"] = now

        PaymentRepository.update_payment(
            target_payment["payment_id"],
            target_payment,
        )

        reservation_id = target_payment["reservation_id"]

        ReservationService.change_reservation_state(
            reservation_id,
            "REFUNDED",
        )

        logger.info(
            "payment_refunded",
            reservation_id=reservation_id,
            payment_id=target_payment["payment_id"],
            refund_id=refund["id"],
            timestamp=now,
        )

        return {
            "payment_id": target_payment["payment_id"],
            "reservation_id": reservation_id,
            "refund_id": refund["id"],
            "amount_refunded": amount,
            "currency": currency,
            "status": "REFUNDED",
            "idempotency_key": idempotency_key,
        }