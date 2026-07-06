# hospitality-reservation-payment-agent/core/logging.py
import logging
import structlog

def setup_logging():
    """
    Minimal, structured logging configuration for high observability.
    Configures standard Python logging to feed into structlog's processor chain.
    """
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
