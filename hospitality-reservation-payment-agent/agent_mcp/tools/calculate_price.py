# agent_mcp/tools/calculate_price.py
from datetime import datetime
from services.payment_service import PaymentService

def calculate_price_tool(room_id: str, check_in: str, check_out: str, guests: int) -> dict:
    """
    MCP Tool: Calculate reservation pricing breakdown based on room type, dates, and number of guests.
    """
    total_price = PaymentService.calculate_price(room_id, check_in, check_out)
    
    try:
        date_format = "%Y-%m-%d"
        start_date = datetime.strptime(check_in, date_format)
        end_date = datetime.strptime(check_out, date_format)
        delta = end_date - start_date
        nights = max(1, delta.days)
    except Exception:
        nights = 1

    price_per_night = round(total_price / nights, 2)

    return {
        "room_id": room_id,
        "nights": nights,
        "price_per_night": price_per_night,
        "total_price": total_price,
        "currency": "usd"
    }

