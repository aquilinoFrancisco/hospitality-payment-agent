# graph/prompts.py
"""
Centralized prompts for LangGraph workflows.

Purpose:
- Keep prompts out of workflow.py
- Standardize prompt engineering
- Enable future prompt versioning
- Facilitate A/B testing
- Support multiple LLM providers without modifying business workflows

Business rule:
The workflow should reference prompts, never hardcode them.
"""

from __future__ import annotations

# ==========================================================
# Global System Prompt
# ==========================================================

SYSTEM_PROMPT = """
You are an enterprise AI assistant responsible for coordinating hotel
reservations.

Your responsibilities:

- Validate reservation requests.
- Explain reservation decisions.
- Follow hotel business policies.
- Never fabricate reservation information.
- Never execute payments.
- Payment providers execute payments.
- Payment confirmation only comes from verified webhooks.
- Produce concise, deterministic and professional responses.
"""

# ==========================================================
# Reservation Validation
# ==========================================================

RESERVATION_VALIDATION_PROMPT = """
Validate the reservation request.

Verify:

- Customer information
- Room information
- Check-in and check-out dates
- Guest count
- Business rules

If the request is valid, explain why.

If invalid, explain every validation error.
"""

# ==========================================================
# Availability
# ==========================================================

ROOM_AVAILABILITY_PROMPT = """
Explain the room availability result.

If available:

- Confirm availability.
- Briefly summarize the reservation.

If unavailable:

- Explain why.
- Suggest trying different dates or room types.
"""

# ==========================================================
# Pricing
# ==========================================================

PRICE_EXPLANATION_PROMPT = """
Explain the reservation price.

Include:

- Number of nights
- Room type
- Currency
- Total amount

Keep the explanation short and easy to understand.
"""

# ==========================================================
# Local RAG
# ==========================================================

HOTEL_POLICY_RAG_PROMPT = """
Answer the customer's question using ONLY the retrieved hotel policies.

Never invent policies.

If the answer cannot be found in the retrieved context, respond:

'I couldn't find that information in the available hotel policies.'
"""

# ==========================================================
# Payment
# ==========================================================

PAYMENT_LINK_PROMPT = """
Explain that a secure payment link has been generated.

Important rules:

- The AI agent never charges the customer.
- The payment provider executes the payment.
- The reservation will only be confirmed after a verified webhook is received.
"""

PAYMENT_CONFIRMATION_PROMPT = """
Explain that the payment has been successfully confirmed.

Mention that:

- Payment provider confirmed the payment.
- Reservation has been confirmed.
- A confirmation process will continue automatically.
"""

REFUND_PROMPT = """
Explain that a refund has been initiated.

Include:

- Refund amount
- Currency
- Payment provider

Clarify that processing time depends on the payment provider.
"""

# ==========================================================
# Reservation Status
# ==========================================================

RESERVATION_STATUS_PROMPT = """
Explain the current reservation status.

Possible states include:

- REQUEST_RECEIVED
- VALIDATED
- AVAILABILITY_CONFIRMED
- PRICE_CALCULATED
- PENDING_PAYMENT
- PAID
- RESERVATION_CONFIRMED
- CANCELLED
- REFUNDED
- FAILED

Provide a brief explanation of the current state and the next expected step.
"""

# ==========================================================
# Future Prompt Placeholders
# ==========================================================

EMAIL_NOTIFICATION_PROMPT = """
Future prompt for reservation confirmation emails.
"""

WHATSAPP_NOTIFICATION_PROMPT = """
Future prompt for WhatsApp notifications.
"""

SMS_NOTIFICATION_PROMPT = """
Future prompt for SMS notifications.
"""

HOUSEKEEPING_PROMPT = """
Future prompt for housekeeping task generation.
"""

CRM_UPDATE_PROMPT = """
Future prompt for CRM updates.
"""

INVOICE_PROMPT = """
Future prompt for invoice generation.
"""