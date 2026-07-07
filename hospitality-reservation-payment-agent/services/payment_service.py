# services/payment_service.py
"""
Payment business service.

This service coordinates payment-related business rules using mock JSON
repositories and a provider-agnostic payment integration layer.

Important:
- The AI agent never charges directly.
- The system only creates payment links.
- The payment provider executes the payment.
- Webhook confirmation is the source of truth.
- Every payment operation should be traceable and idempotent.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

import structlog

from integrations.payments import PaymentProviderFactory
from repositories.payment_repository import PaymentRepository
from repositories.reservation_repository import ReservationRepository
from repositories.room_repository import RoomRepository
from services.reservation_service import ReservationService

logger = structlog.get_logger()


class PaymentService:
    """
    Core payment business service.

    The service does not depend directly on Stripe, Conekta or Mercado Pago.
    It depends on the generic PaymentProvider contract through the factory.
    """

    DEFAULT_PROVIDER = "stripe"

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
        provider: str = DEFAULT_PROVIDER,
    ) -> Dict[str, Any]:
        """
        Create a safe payment link using the configured payment provider.

        Supported providers:
        - stripe
        - conekta
        - mercado_pago

        The agent never charges directly.
        The provider generates the checkout/payment link.
        """

        idempotency_key = (
            idempotency_key
            or f"idem_pay_{reservation_id}"
        )

        currency = currency.lower()
        provider = provider.lower()

        logger.info(
            "payment_create_link_called",
            reservation_id=reservation_id,
            amount=amount,
            currency=currency,
            provider=provider,
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
                and payment.get("provider", provider) == provider
            ):
                logger.info(
                    "pending_payment_already_exists",
                    payment_id=payment["payment_id"],
                    reservation_id=reservation_id,
                    provider=provider,
                )

                return {
                    "payment_id": payment["payment_id"],
                    "reservation_id": reservation_id,
                    "payment_link": payment["payment_link"],
                    "payment_session_id": payment["payment_session_id"],
                    "amount": payment.get("amount", amount),
                    "currency": payment.get("currency", currency),
                    "provider": payment.get("provider", provider),
                    "status": payment["status"],
                    "idempotency_key": payment.get(
                        "idempotency_key",
                        idempotency_key,
                    ),
                }

        payment_provider = PaymentProviderFactory.create(provider)

        provider_response = payment_provider.create_payment_link(
            reservation_id=reservation_id,
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        payment_id = provider_response["payment_id"]

payment_session_id = (
    provider_response.get("payment_session_id")
    or provider_response.get("raw_provider_response", {}).get("id")
    or payment_id
)

payment_link = provider_response["payment_link"]

        now = datetime.utcnow().isoformat() + "Z"

        new_payment = {
            "payment_id": payment_id,
            "reservation_id": reservation_id,
            "amount": amount,
            "currency": currency,
            "provider": provider_response["provider"],
            "status": "PENDING",
            "payment_link": payment_link,
            "payment_session_id": payment_session_id,
            "idempotency_key": idempotency_key,
            "provider_response": provider_response,
            "created_at": now,
            "updated_at": now,
        }

        PaymentRepository.create_payment(new_payment)

        target_reservation["payment_link"] = payment_link
        target_reservation["payment_session_id"] = payment_session_id
        target_reservation["payment_provider"] = provider_response["provider"]
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
            provider=provider_response["provider"],
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
            "provider": provider_response["provider"],
            "status": "PENDING",
            "idempotency_key": idempotency_key,
        }

    @staticmethod
    def get_payment_status(
        payment_id: str,
        provider: str = DEFAULT_PROVIDER,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve payment status from local storage and provider abstraction.
        """
        logger.info(
            "payment_status_requested",
            payment_id=payment_id,
            provider=provider,
        )

        local_payment = PaymentRepository.get_payment(payment_id)

        if not local_payment:
            return None

        payment_provider = PaymentProviderFactory.create(
            local_payment.get("provider", provider)
        )

        provider_status = payment_provider.get_payment_status(payment_id)

        return {
            **local_payment,
            "provider_status": provider_status,
        }

    @staticmethod
    def mark_payment_completed(
        payment_session_id: str,
    ) -> Dict[str, Any]:
        """
        Simulate webhook confirmation.

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
            provider=target_payment.get("provider"),
            timestamp=now,
        )

        return {
            "payment_id": target_payment["payment_id"],
            "reservation_id": reservation_id,
            "status": "COMPLETED",
            "currency": target_payment.get("currency", "usd"),
            "provider": target_payment.get("provider"),
            "updated_at": now,
        }

    @staticmethod
    def issue_refund(
        payment_session_id: str,
        amount: float,
        currency: str = "usd",
        idempotency_key: Optional[str] = None,
        provider: str = DEFAULT_PROVIDER,
    ) -> Dict[str, Any]:
        """
        Issue a refund using the same provider used for the payment.
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
            provider=provider,
            idempotency_key=idempotency_key,
        )

        target_payment = PaymentRepository.get_payment_by_session_id(
            payment_session_id
        )

        if not target_payment:
            raise ValueError(
                f"Payment session '{payment_session_id}' not found."
            )

        selected_provider = target_payment.get("provider", provider)

        payment_provider = PaymentProviderFactory.create(selected_provider)

        refund = payment_provider.refund_payment(
            payment_id=target_payment["payment_id"],
            amount=amount,
            currency=currency,
            idempotency_key=idempotency_key,
        )

        now = datetime.utcnow().isoformat() + "Z"

        target_payment["status"] = "REFUNDED"
        target_payment["updated_at"] = now
        target_payment["refund"] = refund

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
            refund_id=refund["refund_id"],
            provider=selected_provider,
            timestamp=now,
        )

        return {
            "payment_id": target_payment["payment_id"],
            "reservation_id": reservation_id,
            "refund_id": refund["refund_id"],
            "amount_refunded": amount,
            "currency": currency,
            "provider": selected_provider,
            "status": "REFUNDED",
            "idempotency_key": idempotency_key,
        }