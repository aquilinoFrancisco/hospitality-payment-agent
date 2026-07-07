# Hospitality Reservation Payment Flow

## Overview

The Hospitality Reservation Payment Agent follows an **event-driven, provider-agnostic payment architecture**.

Business principles:

- AI agents never charge customers directly.
- AI agents only generate secure payment links.
- Payment providers execute the payment.
- Payment provider webhooks are the single source of truth.
- Every payment operation is idempotent and fully auditable.
- Human confirmation is required before payment.

---

# Supported Payment Providers

The architecture supports multiple payment providers through a common interface.

Current providers:

| Provider | Status | Country |
|----------|--------|----------|
| Stripe Sandbox | ✅ Supported | Global |
| Conekta Sandbox | ✅ Supported | Mexico |
| Mercado Pago Sandbox | ✅ Supported | LATAM |

Future providers can be added without modifying the business workflow.

Examples:

- Adyen
- PayPal
- Square
- OpenPay
- Amazon Pay

---

# Payment Workflow

```text
Customer

↓

FastAPI

↓

LangGraph

↓

CrewAI Reservation Agent

↓

CrewAI Payment Agent

↓

MCP Tool:
create_payment_link()

↓

PaymentService

↓

PaymentProviderFactory

↓

Stripe
Conekta
Mercado Pago

↓

Customer completes payment

↓

Webhook

↓

Reservation confirmed
```

---

# Reservation State Machine

```
REQUEST_RECEIVED
        ↓
VALIDATED
        ↓
AVAILABILITY_CONFIRMED
        ↓
PRICE_CALCULATED
        ↓
PENDING_PAYMENT
       ↙        ↘
FAILED        PAID
                 ↓
RESERVATION_CONFIRMED
        ↓
CANCELLED
        ↓
REFUNDED
```

---

# Reservation State Definitions

### REQUEST_RECEIVED

The reservation request has been received and assigned a unique identifier.

---

### VALIDATED

Customer information, dates and business rules have been validated.

---

### AVAILABILITY_CONFIRMED

The requested room is available.

---

### PRICE_CALCULATED

The reservation amount has been calculated.

---

### PENDING_PAYMENT

A secure payment link has been generated.

The customer must complete the payment using the selected payment provider.

The AI Agent never executes the payment.

---

### PAID

The payment provider confirms that payment was completed successfully.

This state can only be reached through a verified webhook.

---

### RESERVATION_CONFIRMED

The reservation becomes active.

---

### CANCELLED

The reservation was cancelled by the customer or by business rules.

---

### REFUNDED

The payment provider successfully completed the refund.

---

### FAILED

Unexpected validation or system error.

---

# Security Principles

## 1. Provider Agnostic Architecture

Business logic never depends on Stripe, Conekta or Mercado Pago.

Only PaymentProvider implementations know provider-specific APIs.

---

## 2. Human In The Loop

Customers explicitly confirm payment before any transaction occurs.

---

## 3. Idempotency

Every payment operation includes an idempotency key.

This prevents duplicate charges.

---

## 4. Webhooks are the Source of Truth

Reservation status never changes because of frontend requests.

Only verified payment-provider webhooks can transition:

```
PENDING_PAYMENT
        ↓
PAID
        ↓
RESERVATION_CONFIRMED
```

---

## 5. Full Auditability

Every payment operation records:

- Reservation ID
- Payment ID
- Provider
- Currency
- Idempotency Key
- Timestamp
- Reservation State

---

# Multi-Country Configuration

The platform supports country-based payment configuration.

Example:

| Country | Currency | Provider |
|----------|----------|----------|
| Mexico | MXN | Conekta |
| United States | USD | Stripe |
| Spain | EUR | Stripe |
| Argentina | ARS | Mercado Pago |
| Brazil | BRL | Mercado Pago |

Future LangGraph workflows may automatically select the optimal provider using these business rules.

---

# Future Roadmap

Future versions of the platform will support an event-driven post-payment workflow.

```
Webhook

↓

LangGraph

↓

Evaluate Post-Payment Actions

↓

Notification Agent

├── Email
├── WhatsApp
├── SMS
├── CRM Update
├── Housekeeping
└── Invoice Generation
```

The payment provider confirms the transaction.

LangGraph decides which operational actions should execute next.

This keeps payment processing completely independent from business automation.