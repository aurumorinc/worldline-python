# tests/unit/python_logging/test_config.py
import os
from unittest import mock

from python_logging.config import LoggingSettings, StdoutFormat


def test_default_settings():
    """Test that default settings are correctly applied."""
    settings = LoggingSettings()
    assert settings.log_level == "INFO"
    assert settings.stdout_format == StdoutFormat.CONSOLE_RENDERER
    assert settings.otel_exporter_otlp_endpoint is None
    assert settings.otel_exporter_otlp_logs_endpoint is None
    assert settings.traceparent is None


@mock.patch.dict(
    os.environ,
    {
        "LOG_LEVEL": "DEBUG",
        "STDOUT_FORMAT": "rich",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317",
        "TRACEPARENT": "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01",
    },
    clear=True,
)
def test_settings_from_env():
    """Test that settings are correctly loaded from environment variables."""
    settings = LoggingSettings()
    assert settings.log_level == "DEBUG"
    assert settings.stdout_format == StdoutFormat.RICH
    assert settings.otel_exporter_otlp_endpoint == "http://localhost:4317"
    assert settings.traceparent == "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"
