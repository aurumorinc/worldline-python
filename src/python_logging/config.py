# src/python_logging/config.py
import secrets
from enum import Enum
from typing import Optional

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def generate_traceparent() -> str:
    """Generates a valid W3C traceparent string."""
    trace_id = secrets.token_hex(16)
    span_id = secrets.token_hex(8)
    return f"00-{trace_id}-{span_id}-01"


def resolve_traceparent() -> str:
    """
    Resolves the traceparent according to precedence:
    1. Windmill environment variable (WM_TRACEPARENT)
    2. Generated fallback
    """
    from python_logging.integrations.windmill import get_windmill_traceparent

    wm_tp = get_windmill_traceparent()
    if wm_tp:
        return wm_tp
    return generate_traceparent()


class StdoutFormat(str, Enum):
    CONSOLE_RENDERER = "ConsoleRenderer"
    RICH = "rich"


class LoggingSettings(BaseSettings):
    """Configuration for the python-logging package."""

    log_level: str = "INFO"
    stdout_format: StdoutFormat = StdoutFormat.CONSOLE_RENDERER
    otel_exporter_otlp_endpoint: Optional[str] = None
    otel_exporter_otlp_logs_endpoint: Optional[str] = None
    traceparent: str = Field(default_factory=resolve_traceparent)

    @computed_field
    @property
    def trace_id(self) -> str:
        """Extracts the trace_id from the traceparent."""
        return self.traceparent.split("-")[1]

    @computed_field
    @property
    def span_id(self) -> str:
        """Extracts the span_id from the traceparent."""
        return self.traceparent.split("-")[2]

    model_config = SettingsConfigDict()


settings = LoggingSettings()
