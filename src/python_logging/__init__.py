# src/python_logging/__init__.py
from python_logging import config
from python_logging import integrations
from python_logging import main
from python_logging import service

from python_logging.config import (
    LoggingSettings,
    StdoutFormat,
    settings,
)
from python_logging.integrations import (
    get_windmill_context,
    windmill,
)
from python_logging.main import (
    get_logger,
    setup_logging,
)
from python_logging.service import (
    add_otel_context,
    get_console_renderer_format,
    get_rich_format,
    setup_otel_provider,
)

__all__ = [
    "LoggingSettings",
    "StdoutFormat",
    "add_otel_context",
    "config",
    "get_console_renderer_format",
    "get_logger",
    "get_rich_format",
    "get_windmill_context",
    "integrations",
    "main",
    "service",
    "settings",
    "setup_logging",
    "setup_otel_provider",
    "windmill",
]
