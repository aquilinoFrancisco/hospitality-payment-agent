# repositories/payment_repository.py

"""
Payment Repository.

Responsibilities:
- Persist payment transactions.
- Validate minimum payment metadata.
- Keep the repository provider-agnostic.
- Act as the payment ledger for the MVP.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

MOCK_DATA_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "mock_data",
    )
)


def _payments_file() -> str:
    return os.path.join(
        MOCK_DATA_DIR,
        "payments.json",
    )


def _load_payments() -> List[Dict[str, Any]]:
    filepath = _payments_file()

    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return []


def _save_payments(payments: List[Dict[str, Any]]) -> None:
    filepath = _payments_file()

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(
            payments,
            f,
            indent=2,
            ensure_ascii=False,
        )


class PaymentRepository:
    """
    Repository for payment transactions.

    Required payment fields:

    - payment_id
    - reservation_id
    - provider
    - currency
    - payment_session_id
    - idempotency_key
    - amount
    - status
    - created_at
    - updated_at
    """

    REQUIRED_FIELDS = {
        "payment_id",
        "reservation_id",
        "provider",
        "currency",
        "payment_session_id",
        "idempotency_key",
        "amount",
        "status",
        "created_at",
        "updated_at",
    }

    @staticmethod
    def get_payment(
        payment_id: str,
    ) -> Optional[Dict[str, Any]]:

        for payment in _load_payments():

            if payment.get("payment_id") == payment_id:
                return payment

        return None

    @staticmethod
    def get_payment_by_session_id(
        payment_session_id: str,
    ) -> Optional[Dict[str, Any]]:

        for payment in _load_payments():

            if payment.get("payment_session_id") == payment_session_id:
                return payment

        return None

    @staticmethod
    def create_payment(
        payment_data: Dict[str, Any],
    ) -> Dict[str, Any]:

        missing = PaymentRepository.REQUIRED_FIELDS - payment_data.keys()

        if missing:
            raise ValueError(
                f"Missing required payment fields: {sorted(missing)}"
            )

        payments = _load_payments()

        payments.append(payment_data)

        _save_payments(payments)

        return payment_data

    @staticmethod
    def update_payment(
        payment_id: str,
        payment_data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:

        payment_data["updated_at"] = (
            datetime.utcnow().isoformat() + "Z"
        )

        missing = PaymentRepository.REQUIRED_FIELDS - payment_data.keys()

        if missing:
            raise ValueError(
                f"Missing required payment fields: {sorted(missing)}"
            )

        payments = _load_payments()

        for index, payment in enumerate(payments):

            if payment.get("payment_id") == payment_id:

                payments[index] = payment_data

                _save_payments(payments)

                return payment_data

        return None

    @staticmethod
    def list_payments() -> List[Dict[str, Any]]:
        return _load_payments()