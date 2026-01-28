"""
Structured logging configuration for Ashlag Yomi.

Uses structlog for structured, machine-readable logs that are:
- Easy to parse in production (JSON format)
- Beautiful in development (colored, formatted)
- Context-rich (automatic timestamps, log levels, etc.)

Usage:
    from src.utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("sending_quote", rabbi="Baal HaSulam", quote_id="abc123")
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from src.utils.config import get_settings


def setup_logging() -> None:
    """
    Configure structured logging for the application.

    Call this once at application startup (in main.py).
    """
    settings = get_settings()

    # Determine if we want pretty (dev) or JSON (prod) output
    is_development = settings.is_development

    # Shared processors for all environments
    shared_processors: list[Processor] = [
        # Add log level as a string
        structlog.stdlib.add_log_level,
        # Add timestamp
        structlog.processors.TimeStamper(fmt="iso"),
        # Add stack info for exceptions
        structlog.processors.StackInfoRenderer(),
        # Format exceptions nicely
        structlog.processors.format_exc_info,
        # Handle Unicode properly (important for Hebrew!)
        structlog.processors.UnicodeDecoder(),
    ]

    if is_development:
        # Development: Pretty, colored console output
        processors: list[Processor] = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
            ),
        ]
    else:
        # Production: JSON output for log aggregation
        processors = [
            *shared_processors,
            # Prepare for JSON serialization
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Also configure standard library logging (for third-party libs)
    logging.basicConfig(
        format="%(message)s",
        level=settings.log_level,
        stream=sys.stdout,
    )

    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> Any:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__). If None, returns root logger.

    Returns:
        A bound structlog logger

    Example:
        logger = get_logger(__name__)
        logger.info("processing_quote", rabbi="Rabash", length=150)

        # Output (dev):
        # 2024-01-15T10:30:00 [info] processing_quote rabbi=Rabash length=150

        # Output (prod):
        # {"event": "processing_quote", "rabbi": "Rabash", "length": 150, ...}
    """
    return structlog.get_logger(name)


def log_context(**kwargs: Any) -> structlog.contextvars.bound_contextvars:
    """
    Create a context manager that binds variables to all logs within it.

    Useful for adding request-scoped context (like a trace_id) to all logs.

    Args:
        **kwargs: Key-value pairs to bind to log context

    Example:
        with log_context(request_id="abc123", user="@john"):
            logger.info("starting_task")  # includes request_id and user
            do_something()
            logger.info("finished_task")  # also includes request_id and user
    """
    return structlog.contextvars.bound_contextvars(**kwargs)
