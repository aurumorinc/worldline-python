# src/worldline/config.py
import os
import secrets
from typing import Any, Optional

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
    from worldline.integrations.windmill import get_windmill_traceparent

    windmill_tp = get_windmill_traceparent()
    if windmill_tp:
        return windmill_tp
    return generate_traceparent()


class WorldlineSettings(BaseSettings):
    """Configuration for the lume package."""

    log_level: str = "INFO"
    otel_exporter_otlp_endpoint: Optional[str] = None
    otel_exporter_otlp_logs_endpoint: Optional[str] = None
    traceparent: str = Field(default_factory=resolve_traceparent)

    sentry_dsn: Optional[str] = None

    posthog_api_key: Optional[str] = None
    posthog_host: str = "https://us.i.posthog.com"

    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    langfuse_base_url: str = "https://cloud.langfuse.com"
    langfuse_host: Optional[str] = None

    windmill_token: Optional[str] = None
    windmill_workspace: Optional[str] = None
    windmill_base_url: Optional[str] = None

    @computed_field  # type: ignore
    @property
    def is_windmill_env(self) -> bool:
        return bool(self.windmill_token and self.windmill_workspace)

    @computed_field  # type: ignore
    @property
    def trace_id(self) -> str:
        """Extracts the trace_id from the traceparent."""
        return self.traceparent.split("-")[1]

    @computed_field  # type: ignore
    @property
    def span_id(self) -> str:
        """Extracts the span_id from the traceparent."""
        return self.traceparent.split("-")[2]

    model_config = SettingsConfigDict()

    def model_post_init(self, __context: Any) -> None:
        """Propagate settings to environment variables for native SDKs to pick up."""
        if self.langfuse_public_key:
            os.environ["LANGFUSE_PUBLIC_KEY"] = self.langfuse_public_key
        if self.langfuse_secret_key:
            os.environ["LANGFUSE_SECRET_KEY"] = self.langfuse_secret_key
        
        active_url = self.langfuse_host or self.langfuse_base_url
        if active_url:
            os.environ["LANGFUSE_BASE_URL"] = active_url
            os.environ["LANGFUSE_HOST"] = active_url

        if self.posthog_api_key:
            os.environ["POSTHOG_API_KEY"] = self.posthog_api_key
        if self.posthog_host:
            os.environ["POSTHOG_HOST"] = self.posthog_host

        if self.sentry_dsn:
            os.environ["SENTRY_DSN"] = self.sentry_dsn


settings = WorldlineSettings()
