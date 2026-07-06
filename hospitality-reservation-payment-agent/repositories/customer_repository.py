# repositories/customer_repository.py
import os
import json
from typing import Dict, Any, List, Optional

MOCK_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mock_data"))

def _load_customers() -> List[Dict[str, Any]]:
    filepath = os.path.join(MOCK_DATA_DIR, "customers.json")
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception:
        return []

def _save_customers(customers: List[Dict[str, Any]]):
    filepath = os.path.join(MOCK_DATA_DIR, "customers.json")
    try:
        with open(filepath, "w") as f:
            json.dump(customers, f, indent=2)
    except Exception:
        pass

class CustomerRepository:
    """
    Data Access Object for customers.json dataset.
    Strictly handles database loading and saving of customer details.
    """

    @staticmethod
    def get_customer(customer_id: str) -> Optional[Dict[str, Any]]:
        customers = _load_customers()
        for c in customers:
            if c["id"] == customer_id:
                return c
        return None

    @staticmethod
    def get_customer_by_email(email: str) -> Optional[Dict[str, Any]]:
        customers = _load_customers()
        for c in customers:
            if c["email"].strip().lower() == email.strip().lower():
                return c
        return None

    @staticmethod
    def get_all_customers() -> List[Dict[str, Any]]:
        return _load_customers()

    @staticmethod
    def create_customer(customer_data: Dict[str, Any]) -> Dict[str, Any]:
        customers = _load_customers()
        customers.append(customer_data)
        _save_customers(customers)
        return customer_data
