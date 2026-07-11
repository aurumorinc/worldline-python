# src/worldline/integrations/structlog.py
"""
structlog configuration logic.
"""

import logging
from typing import TYPE_CHECKING, Any, List, Optional

import structlog

if TYPE_CHECKING:
    from worldline.config import WorldlineSettings


def setup_structlog(settings: Optional["WorldlineSettings"] = None) -> None:
    """
    Internal zero-config initialization.
    Configures structlog and routes standard logging through it.
    """
    if settings is None:
        from worldline.config import settings as default_settings

        settings = default_settings

    # Determine log level
    log_level_name = settings.log_level.upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    # Shared processors
    from worldline.service import (
        add_otel_context,
        get_console_format,
        setup_otel_provider,
    )

    shared_processors: List[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        add_otel_context,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    format_processors, handlers = get_console_format()

    # Configure structlog
    structlog_processors = shared_processors + [
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter
    ]

    structlog.configure(
        processors=structlog_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard logging handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(log_level)

    # Add stdout transport handlers
    for handler in handlers:
        formatter = structlog.stdlib.ProcessorFormatter(
            processors=format_processors,
            foreign_pre_chain=shared_processors,
        )
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    # 4. Windmill OTEL Logic
    logger_provider = setup_otel_provider(settings)
    if logger_provider:
        from opentelemetry.sdk._logs import LoggingHandler

        otlp_handler = LoggingHandler(level=log_level, logger_provider=logger_provider)
        root_logger.addHandler(otlp_handler)
