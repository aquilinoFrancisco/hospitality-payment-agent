# Model Context Protocol (MCP) Tools Documentation

The hospitality agent platform implements a decoupled **Model Context Protocol (MCP)** tools layer. The core coordinator class is `MCPServer` (defined in `agent_mcp/server.py`), which acts as the registry routing tool-calls from the LLM or orchestration agents directly to our core business services.

This design completely decouples agent prompt engineering and framework execution from underlying service-oriented business logic.

---

## Architectural Position

```
    LLM / Agentic Prompt (CrewAI, LangGraph)
                     │
                     ▼
          [ MCP Server Registry ]
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
  [Tool A]        [Tool B]      [Tool C] ... (8 Registered Tools)
       │             │             │
       └─────────────┼─────────────┘
                     ▼
             [ Business Services ]
                     │
                     ▼
              [ Repositories ]
                     │
                     ▼
               [ Mock JSON ]
```

---

## The `MCPServer` Interface

The `MCPServer` exposes two high-level interfaces:

### 1. `list_tools()`
Returns a list of metadata for all registered tools, including names, human descriptions, and input schemas for LLM routing.

### 2. `call_tool(tool_name: str, **kwargs)`
Invokes the respective tool by its name, handles arguments injection safely, captures exceptions, and returns clean, auditable, JSON-safe dictionaries.

```python
from agent_mcp.server import MCPServer

server = MCPServer()

# Check what tools are available
tools_list = server.list_tools()

# Execute a tool
result = server.call_tool(
    "check_availability",
    room_id="deluxe-suite",
    check_in="2026-07-10",
    check_out="2026-07-15"
)
```

---

## Detailed Tool Specification

### 1. `check_availability`
- **Description:** Verifies calendar occupancy in the mock database.
- **Input Parameters:**
  - `room_id` (string): Target room identifier (e.g. `"deluxe-suite"`).
  - `check_in` (string): Date formatted as `YYYY-MM-DD`.
  - `check_out` (string): Date formatted as `YYYY-MM-DD`.
- **Output Schema:**
  ```json
  {
    "available": true,
    "room_id": "deluxe-suite",
    "check_in": "2026-07-10",
    "check_out": "2026-07-15",
    "message": "Room 'deluxe-suite' is available from 2026-07-10 to 2026-07-15."
  }
  ```

### 2. `calculate_price`
- **Description:** Calculates total booking rates and subtotal nights.
- **Input Parameters:**
  - `room_id` (string): Target room identifier.
  - `check_in` (string): Format `YYYY-MM-DD`.
  - `check_out` (string): Format `YYYY-MM-DD`.
  - `guests` (integer): Number of staying guests.
- **Output Schema:**
  ```json
  {
    "room_id": "deluxe-suite",
    "nights": 5,
    "price_per_night": 250.0,
    "total_price": 1250.0,
    "currency": "usd"
  }
  ```

### 3. `create_payment_link`
- **Description:** Requests Stripe Sandbox checkout URL. Transition reservation state to `PENDING_PAYMENT`.
- **Input Parameters:**
  - `reservation_id` (string): Booking ID.
  - `amount` (number): Price subtotal.
  - `currency` (string): Default is `"usd"`.
- **Output Schema:**
  ```json
  {
    "payment_id": "pay_mock_12345",
    "reservation_id": "res_98765",
    "payment_link": "https://sandbox.stripe.com/checkout/mock_session_res_98765",
    "status": "PENDING",
    "idempotency_key": "idem_pay_res_98765"
  }
  ```

### 4. `check_payment_status`
- **Description:** Queries tracking logs for checkout paid status.
- **Input Parameters:**
  - `payment_id` (string): Payment transaction code.
- **Output Schema:**
  ```json
  {
    "payment_id": "pay_mock_12345",
    "reservation_id": "res_98765",
    "status": "PAID"
  }
  ```

### 5. `confirm_reservation`
- **Description:** Moves reservation records from `PENDING_PAYMENT` to `RESERVATION_CONFIRMED` upon verified payments.
- **Input Parameters:**
  - `reservation_id` (string): Booking ID.
- **Output Schema:**
  ```json
  {
    "reservation_id": "res_98765",
    "reservation_state": "RESERVATION_CONFIRMED",
    "message": "Reservation 'res_98765' has been successfully confirmed."
  }
  ```

### 6. `cancel_reservation`
- **Description:** Cancels booking and releases blocked calendar dates.
- **Input Parameters:**
  - `reservation_id` (string): Booking ID.
  - `reason` (string): Explanation text.
- **Output Schema:**
  ```json
  {
    "reservation_id": "res_98765",
    "reservation_state": "CANCELLED",
    "cancellation_reason": "Guest schedule change",
    "message": "Reservation 'res_98765' has been successfully cancelled. Reason: Guest schedule change."
  }
  ```

### 7. `issue_refund`
- **Description:** Triggers a safe refund sandboxed transaction.
- **Input Parameters:**
  - `payment_id` (string): Transaction ID.
  - `reason` (string): Return reason.
- **Output Schema:**
  ```json
  {
    "payment_id": "pay_mock_12345",
    "refund_id": "ref_pay_mock_12345",
    "status": "REFUNDED",
    "reason": "Duplicate booking",
    "message": "Refund of $1250.00 processed successfully for payment 'pay_mock_12345'."
  }
  ```

### 8. `save_reservation_report`
- **Description:** Saves structural JSON receipt report to the local `/reports` folder.
- **Input Parameters:**
  - `report_payload` (dict): Nested JSON payload metadata.
- **Output Schema:**
  ```json
  {
    "report_id": "res_98765",
    "file_path": "reports/report_res_98765.json",
    "status": "SAVED"
  }
  ```
