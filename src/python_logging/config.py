# src/python_logging/config.py
from enum import Enum
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class StdoutFormat(str, Enum):
    CONSOLE_RENDERER = "ConsoleRenderer"
    RICH = "rich"


class LoggingSettings(BaseSettings):
    """Configuration for the python-logging package."""

    log_level: str = "INFO"
    stdout_format: StdoutFormat = StdoutFormat.CONSOLE_RENDERER
    otel_exporter_otlp_endpoint: Optional[str] = None
    otel_exporter_otlp_logs_endpoint: Optional[str] = None
    traceparent: Optional[str] = None

    model_config = SettingsConfigDict()


settings = LoggingSettings()
