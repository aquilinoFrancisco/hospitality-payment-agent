# Stripe Sandbox Payment Flow

We adhere to rigorous **auditable payment security principles**:

1. **Indirect Charging**: Agents never handle primary card holder data directly. The agent generates a checkout link.
2. **Checkout Sandbox**: Payment is completed in Stripe Sandbox.
3. **Idempotency Key Verification**: Every transactional session includes an `idempotency_key` to avoid duplicate billing.
4. **Webhook Source of Truth**: Success state transitions are exclusively driven by Stripe webhook callbacks (`checkout.session.completed`), not frontend clients.
5. **Human-in-the-Loop**: Confirmations are explicitly required prior to locking down reservations and issuing payouts.

---

## 🔄 Reservation State Machine Lifecycle

The reservation state is moved deterministically through the following logical transitions:

```
[REQUEST_RECEIVED]
       ↓
  [VALIDATED]
       ↓
[AVAILABILITY_CONFIRMED]
       ↓
[PRICE_CALCULATED]
       ↓
[PENDING_PAYMENT]   ───► [FAILED]
       ↓
     [PAID]         ───► [REFUNDED]
       ↓
[RESERVATION_CONFIRMED] ───► [CANCELLED]
```

### State Definitions:
- **`REQUEST_RECEIVED`**: The draft booking has been requested and assigned a unique tracking ID.
- **`VALIDATED`**: The customer details and dates have passed syntax checks.
- **`AVAILABILITY_CONFIRMED`**: Room calendars are checked and blocked to prevent double-booking.
- **`PRICE_CALCULATED`**: Exact pricing is computed (base price × nights).
- **`PENDING_PAYMENT`**: A mock Stripe session is registered and checkout link (`https://sandbox.stripe.com/pay/demo-payment-XXX`) is returned to the user.
- **`PAID`**: Stripe webhooks confirm successful charge capture.
- **`RESERVATION_CONFIRMED`**: Booking calendar locks are officially committed.
- **`CANCELLED`**: Booking aborted by user or timeout.
- **`REFUNDED`**: Reversal processed successfully.
- **`FAILED`**: System or validation error occurred.
