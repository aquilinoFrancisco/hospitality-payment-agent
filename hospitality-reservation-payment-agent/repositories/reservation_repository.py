# repositories/reservation_repository.py
import os
import json
from typing import Dict, Any, List, Optional

MOCK_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mock_data"))

def _load_reservations() -> List[Dict[str, Any]]:
    filepath = os.path.join(MOCK_DATA_DIR, "reservations.json")
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception:
        return []

def _save_reservations(reservations: List[Dict[str, Any]]):
    filepath = os.path.join(MOCK_DATA_DIR, "reservations.json")
    try:
        with open(filepath, "w") as f:
            json.dump(reservations, f, indent=2)
    except Exception:
        pass

class ReservationRepository:
    """
    Data Access Object for reservations.json dataset.
    Strictly handles database reading and writing of reservation records.
    """

    @staticmethod
    def get_reservation(reservation_id: str) -> Optional[Dict[str, Any]]:
        reservations = _load_reservations()
        for r in reservations:
           if r.get("reservation_id") == reservation_id: 
                return r
        return None

    @staticmethod
    def create_reservation(reservation_data: Dict[str, Any]) -> Dict[str, Any]:
        reservations = _load_reservations()
        reservations.append(reservation_data)
        _save_reservations(reservations)
        return reservation_data

    @staticmethod
    def update_reservation(reservation_id: str, reservation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        reservations = _load_reservations()
        for i, r in enumerate(reservations):
            if r.get("reservation_id") == reservation_id:
                reservations[i] = reservation_data
                _save_reservations(reservations)
                return reservation_data
        return None

    @staticmethod
    def list_reservations() -> List[Dict[str, Any]]:
        return _load_reservations()

    @staticmethod
    def get_availability_records() -> List[Dict[str, Any]]:
        filepath = os.path.join(MOCK_DATA_DIR, "availability.json")
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception:
            return []
