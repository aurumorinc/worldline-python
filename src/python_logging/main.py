# src/python_logging/main.py
import logging
from typing import Optional

import structlog
from opentelemetry.sdk._logs import LoggingHandler

from python_logging.config import (
    LoggingSettings,
    StdoutFormat,
    settings as default_settings,
)
from python_logging.service import (
    add_otel_context,
    get_console_renderer_format,
    get_rich_format,
    setup_otel_provider,
)

# Export get_logger for use throughout the application
get_logger = structlog.get_logger


def setup_logging(settings: Optional[LoggingSettings] = None) -> None:
    """
    Configures structlog and routes standard logging through it.
    Uses the provided settings or the global default settings.
    """
    if settings is None:
        settings = default_settings

    # Determine log level
    log_level_name = settings.log_level.upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    # Shared processors for all formats
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        add_otel_context,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Get format-specific processors and handlers for the stdout transport
    if settings.stdout_format == StdoutFormat.RICH:
        format_processors, handlers = get_rich_format()
    else:
        format_processors, handlers = get_console_renderer_format()

    # Configure structlog
    if settings.stdout_format == StdoutFormat.RICH:
        structlog_processors = shared_processors + format_processors
    else:
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
        # For non-Rich formats, we need to wrap the handler with structlog's formatter
        if settings.stdout_format != StdoutFormat.RICH:
            formatter = structlog.stdlib.ProcessorFormatter(
                processors=format_processors,
                foreign_pre_chain=shared_processors,
            )
            handler.setFormatter(formatter)

        root_logger.addHandler(handler)

    # Setup OpenTelemetry OTLP transport if configured
    logger_provider = setup_otel_provider()
    if logger_provider:
        otlp_handler = LoggingHandler(level=log_level, logger_provider=logger_provider)
        root_logger.addHandler(otlp_handler)
