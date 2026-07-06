# repositories/payment_repository.py
import os
import json
from typing import Dict, Any, List, Optional

MOCK_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mock_data"))

def _load_payments() -> List[Dict[str, Any]]:
    filepath = os.path.join(MOCK_DATA_DIR, "payments.json")
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception:
        return []

def _save_payments(payments: List[Dict[str, Any]]):
    filepath = os.path.join(MOCK_DATA_DIR, "payments.json")
    try:
        with open(filepath, "w") as f:
            json.dump(payments, f, indent=2)
    except Exception:
        pass

class PaymentRepository:
    """
    Data Access Object for payments.json dataset.
    Strictly handles database reading and writing of payment ledger transactions.
    """

    @staticmethod
    def get_payment(payment_id: str) -> Optional[Dict[str, Any]]:
        payments = _load_payments()
        for p in payments:
            if p["payment_id"] == payment_id:
                return p
        return None

    @staticmethod
    def get_payment_by_session_id(payment_session_id: str) -> Optional[Dict[str, Any]]:
        payments = _load_payments()
        for p in payments:
            if p["payment_session_id"] == payment_session_id:
                return p
        return None

    @staticmethod
    def create_payment(payment_data: Dict[str, Any]) -> Dict[str, Any]:
        payments = _load_payments()
        payments.append(payment_data)
        _save_payments(payments)
        return payment_data

    @staticmethod
    def update_payment(payment_id: str, payment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        payments = _load_payments()
        for i, p in enumerate(payments):
            if p["payment_id"] == payment_id:
                payments[i] = payment_data
                _save_payments(payments)
                return payment_data
        return None

    @staticmethod
    def list_payments() -> List[Dict[str, Any]]:
        return _load_payments()
