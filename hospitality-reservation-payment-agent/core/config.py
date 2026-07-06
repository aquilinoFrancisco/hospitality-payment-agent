# hospitality-reservation-payment-agent/core/config.py
import os
from pydantic import BaseModel, Field

class Settings(BaseModel):
    """
    Application Settings and Environment Variable Management.
    Kept minimal and easy to explain.
    """
    APP_NAME: str = "Hospitality AI Agent"
    ENV: str = os.getenv("NODE_ENV", "development")
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # API Keys / Integrations (Read from env but safe)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "mock_gemini_key")
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "mock_stripe_key")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "mock_webhook_secret")
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
