# repositories/room_repository.py
import os
import json
from typing import Dict, Any, List, Optional

MOCK_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mock_data"))

def _load_rooms() -> List[Dict[str, Any]]:
    filepath = os.path.join(MOCK_DATA_DIR, "rooms.json")
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception:
        return []

def _save_rooms(rooms: List[Dict[str, Any]]):
    filepath = os.path.join(MOCK_DATA_DIR, "rooms.json")
    try:
        with open(filepath, "w") as f:
            json.dump(rooms, f, indent=2)
    except Exception:
        pass

class RoomRepository:
    """
    Data Access Object for rooms.json dataset.
    Strictly handles read/write mechanics; contains zero business state transition logic.
    """

    @staticmethod
    def get_room(room_id: str) -> Optional[Dict[str, Any]]:
        rooms = _load_rooms()
        for r in rooms:
            if r["id"] == room_id:
                return r
        return None

    @staticmethod
    def get_all_rooms() -> List[Dict[str, Any]]:
        return _load_rooms()

    @staticmethod
    def update_room(room_id: str, room_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        rooms = _load_rooms()
        for i, r in enumerate(rooms):
            if r["id"] == room_id:
                rooms[i] = room_data
                _save_rooms(rooms)
                return room_data
        return None
