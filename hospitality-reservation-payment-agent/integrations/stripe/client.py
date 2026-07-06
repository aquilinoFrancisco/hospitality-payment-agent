# hospitality-reservation-payment-agent/integrations/stripe/client.py
import structlog
from typing import Dict, Any, Optional

logger = structlog.get_logger()

class StripeSandboxClient:
    """
    Stripe Sandbox Client Wrapper.
    Reserved for future Stripe SDK integrations.
    Contains no active SDK initializations, credentials, or production client state.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        logger.info("StripeSandboxClient initialized (placeholder mode)")

    def create_checkout_session(
        self,
        reservation_id: str,
        amount: float,
        idempotency_key: str
    ) -> Dict[str, Any]:
        """
        Prepares standard Stripe API session definitions.
        """
        logger.info(
            "Stripe API Wrapper: mock create_checkout_session invoked",
            reservation_id=reservation_id,
            amount=amount,
            idempotency_key=idempotency_key
        )
        return {
            "id": f"cs_test_mock_{idempotency_key[:8]}",
            "url": f"https://checkout.stripe.com/pay/mock_session_{reservation_id}",
            "amount_total": int(amount * 100),
            "currency": "usd",
            "payment_status": "unpaid",
            "metadata": {
                "reservation_id": reservation_id,
                "idempotency_key": idempotency_key
            }
        }

    def refund_payment(
        self,
        charge_id: str,
        amount: float,
        idempotency_key: str
    ) -> Dict[str, Any]:
        """
        Triggers mock refund with standard metadata tracking.
        """
        logger.info(
            "Stripe API Wrapper: mock refund_payment invoked",
            charge_id=charge_id,
            amount=amount,
            idempotency_key=idempotency_key
        )
        return {
            "id": f"re_test_mock_{idempotency_key[:8]}",
            "amount": int(amount * 100),
            "status": "succeeded",
            "charge": charge_id
        }
