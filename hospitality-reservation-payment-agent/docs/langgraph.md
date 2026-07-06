# LangGraph Workflow Orchestration

Our platform utilizes **LangGraph** as a deterministic, state-driven workflow coordinator. This layer guarantees that reservation requests are systematically validated, verified, priced, and processed prior to initiating payments or involving downstream human-like agents (e.g. CrewAI specialists).

---

## The Core Design Philosophy

### Decoupling Orchestration from Execution

A fundamental architectural constraint of this platform is that **LangGraph nodes are strictly coordinators (orchestrators)**. They do NOT execute business logic, write database records, calculate financial numbers, or handle third-party SDK calls. 

Instead, LangGraph maintains and transitions thread state, making RPC-style tool-calls to the **Model Context Protocol (MCP)** tool layer.

#### Why this separation is vital:
1. **Separation of Concerns:** Keep routing logic separated from core application rules.
2. **Reusability:** Business tools can be called by diverse interfaces (REST APIs, CLI, CrewAI agents, or LangGraph) identically.
3. **Auditability:** Every system transition and API/tool call logs structured events, making failure analysis straightforward.
4. **Deterministic Gatekeeping:** Ensuring that expensive operations are only reached if previous validations pass.

---

## State Definition (`ReservationState`)

The state of our workflow is tracked inside a standard `TypedDict` containing transaction-specific fields:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `reservation_id` | `Optional[str]` | The unique system identifier for the reservation. Generated on demand if missing. |
| `customer_id` | `Optional[str]` | Identifier tracking the requesting guest. |
| `room_id` | `Optional[str]` | The selected room category code (e.g. `"deluxe-suite"`). |
| `check_in` | `Optional[str]` | Check-in date formatted as `YYYY-MM-DD`. |
| `check_out` | `Optional[str]` | Check-out date formatted as `YYYY-MM-DD`. |
| `guests` | `Optional[int]` | Count of staying guests. |
| `reservation_state` | `Optional[str]` | Orchestrated stage status (e.g. `"VALIDATED"`, `"AVAILABILITY_CONFIRMED"`, `"PRICE_CALCULATED"`, `"PENDING_PAYMENT"`, `"FAILED"`). |
| `payment_state` | `Optional[str]` | Current transaction checkout state (e.g. `"PENDING"`, `"PAID"`). |
| `payment_link` | `Optional[str]` | The generated Stripe Checkout sandbox transaction URL. |
| `payment_id` | `Optional[str]` | Sandbox payment transaction reference. |
| `total_price` | `Optional[float]`| The calculated reservation cost subtotal. |
| `currency` | `Optional[str]` | ISO currency code (e.g. `"usd"`). |
| `messages` | `List[str]` | Sequential list of user-facing status messages appended throughout execution. |
| `error` | `Optional[str]` | Detailed explanation of error if a node or tool execution fails. |

---

## Workflow Graph Nodes

The graph comprises 5 sequential nodes:

```
[START]
   │
   ▼
[validate_request] ──(fail)──► [END]
   │ (pass)
   ▼
[check_availability] ──(fail)──► [END]
   │ (pass)
   ▼
[calculate_price] ──(fail)──► [END]
   │ (pass)
   ▼
[create_payment_link] ──(fail)──► [END]
   │ (pass)
   ▼
[finish]
   │
   ▼
[END]
```

### 1. `validate_request`
- **Role:** Exercises structural format checks on inputs (ensures customer IDs, room IDs, check-in, check-out, and guests count are provided and logically consistent).
- **Result:** Transitions `reservation_state` to `"VALIDATED"` or `"FAILED"`.

### 2. `check_availability`
- **Role:** Invokes the `check_availability` MCP tool to query rooms inventory.
- **Result:** Transitions `reservation_state` to `"AVAILABILITY_CONFIRMED"` or `"FAILED"`.

### 3. `calculate_price`
- **Role:** Invokes the `calculate_price` MCP tool to compute price tiers.
- **Result:** Transitions `reservation_state` to `"PRICE_CALCULATED"` or `"FAILED"`.

### 4. `create_payment_link`
- **Role:** Invokes the `create_payment_link` MCP tool to register payment references.
- **Result:** Transitions `reservation_state` to `"PENDING_PAYMENT"` or `"FAILED"`.

### 5. `finish`
- **Role:** Finalizes successful workflow executions and appends a completion status.
- **Result:** Transitions state safely to `END`.

---

## Conditional Routing & Decision Edges

Deterministic branching is governed by checking the state's `reservation_state` flag at each node exit point. If any step assigns `"FAILED"`, the graph skips remaining operations and immediately routes to `END`.

### Routing Logic:

- **After `validate_request`:**
  - `FAILED` ➔ `END`
  - `VALIDATED` ➔ `check_availability`

- **After `check_availability`:**
  - `FAILED` ➔ `END`
  - `AVAILABILITY_CONFIRMED` ➔ `calculate_price`

- **After `calculate_price`:**
  - `FAILED` ➔ `END`
  - `PRICE_CALCULATED` ➔ `create_payment_link`

- **After `create_payment_link`:**
  - `FAILED` ➔ `END`
  - `PENDING_PAYMENT` ➔ `finish`
