# src/worldline/integrations/structlog.py
"""
Zero-config drop-in replacement proxy for structlog.

Provides automatic initialization of standard logging, OpenTelemetry, Sentry,
PostHog, and Langfuse when requested. Also provides smart merging for
configurations.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import structlog as _original_structlog

# Explicit Proxy Imports to preserve IDE autocomplete and strict static typing.
from structlog import (
    BoundLogger,
    DropEvent,
    PrintLogger,
    ReturnLogger,
    WriteLogger,
    contextvars,
    dev,
    get_config,
    get_context,
    is_configured,
    processors,
    reset_defaults,
    stdlib,
    testing,
    threadlocal,
)

if TYPE_CHECKING:
    from worldline.config import WorldlineSettings

_WORLDLINE_CONFIGURED: bool = False


def _setup(settings: Optional["WorldlineSettings"] = None) -> None:
    """
    Internal zero-config initialization.
    Configures structlog and routes standard logging through it.
    Also initializes Sentry, PostHog, Langfuse, and OpenTelemetry.
    """
    global _WORLDLINE_CONFIGURED
    if _WORLDLINE_CONFIGURED:
        return

    if settings is None:
        from worldline.config import settings as default_settings

        settings = default_settings

    # 1. Sentry Setup
    if settings.sentry_dsn:
        from worldline.integrations.sentry import sentry_sdk

        sentry_sdk.init(dsn=settings.sentry_dsn)

    # 2. PostHog Setup
    if settings.posthog_api_key:
        from worldline.integrations.posthog import posthog

        posthog.project_api_key = settings.posthog_api_key  # type: ignore
        posthog.host = settings.posthog_host  # type: ignore

    # 3. Langfuse Setup
    if settings.langfuse_public_key:
        import langfuse

        langfuse.Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_base_url,
        )

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
        _original_structlog.contextvars.merge_contextvars,
        _original_structlog.stdlib.add_log_level,
        _original_structlog.stdlib.add_logger_name,
        add_otel_context,
        _original_structlog.processors.TimeStamper(fmt="iso"),
        _original_structlog.processors.StackInfoRenderer(),
    ]

    format_processors, handlers = get_console_format()

    # Configure structlog
    structlog_processors = shared_processors + [
        _original_structlog.stdlib.ProcessorFormatter.wrap_for_formatter
    ]

    _original_structlog.configure(
        processors=structlog_processors,
        logger_factory=_original_structlog.stdlib.LoggerFactory(),
        wrapper_class=_original_structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard logging handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(log_level)

    # Add stdout transport handlers
    for handler in handlers:
        formatter = _original_structlog.stdlib.ProcessorFormatter(
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

    _WORLDLINE_CONFIGURED = True


def get_logger(*args: Any, **kwargs: Any) -> Any:
    if not _WORLDLINE_CONFIGURED:
        _setup()
    return _original_structlog.get_logger(*args, **kwargs)


def getLogger(*args: Any, **kwargs: Any) -> Any:
    if not _WORLDLINE_CONFIGURED:
        _setup()
    return _original_structlog.getLogger(*args, **kwargs)


def wrap_logger(logger: Any, **kwargs: Any) -> Any:
    if not _WORLDLINE_CONFIGURED:
        _setup()
    return _original_structlog.wrap_logger(logger, **kwargs)


def _merge_configuration(kwargs: Dict[str, Any], once: bool = False) -> None:
    if not _WORLDLINE_CONFIGURED:
        _setup()

    current_config = _original_structlog.get_config()

    if "processors" in kwargs:
        user_processors = kwargs.pop("processors")
        current_processors = list(current_config.get("processors", []))

        # In setup, the last processor is usually wrap_for_formatter or similar finalizer
        if current_processors:
            formatter = current_processors.pop()
            merged_processors = current_processors + user_processors + [formatter]
        else:
            merged_processors = user_processors

        kwargs["processors"] = merged_processors

    current_config.update(kwargs)

    # We must call reset_defaults if not configuring once, but we shouldn't wipe our setup.
    # structlog.configure overwrites, but structlog prevents multiple calls unless reset or configure_once.
    # We'll just call reset_defaults so we don't get the configuration exception, then configure.
    if not once:
        _original_structlog.reset_defaults()
        _original_structlog.configure(**current_config)
    else:
        try:
            _original_structlog.configure_once(**current_config)
        except Exception:
            pass  # Already configured


def configure(**kwargs: Any) -> None:
    _merge_configuration(kwargs, once=False)


def configure_once(**kwargs: Any) -> None:
    _merge_configuration(kwargs, once=True)


__all__ = [
    "BoundLogger",
    "DropEvent",
    "PrintLogger",
    "ReturnLogger",
    "WriteLogger",
    "configure",
    "configure_once",
    "contextvars",
    "dev",
    "get_config",
    "get_context",
    "getLogger",
    "get_logger",
    "is_configured",
    "processors",
    "reset_defaults",
    "stdlib",
    "testing",
    "threadlocal",
    "wrap_logger",
]


def __getattr__(name: str) -> Any:
    try:
        return getattr(_original_structlog, name)
    except AttributeError:
        raise AttributeError(f"module 'structlog' has no attribute '{name}'")


def __dir__() -> List[str]:
    return __all__
