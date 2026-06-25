# tests/unit/lume/test_config.py
import os
import re
from unittest import mock
import pytest

from lume.config import LoggingSettings, generate_traceparent


def test_default_settings():
    """Test that default settings are correctly applied and traceparent is generated."""
    # Arrange & Act
    settings = LoggingSettings()

    # Assert
    assert settings.log_level == "INFO"
    assert settings.otel_exporter_otlp_endpoint is None
    assert settings.otel_exporter_otlp_logs_endpoint is None

    # Verify traceparent is generated and matches W3C format
    assert settings.traceparent is not None
    assert re.match(r"^00-[0-9a-f]{32}-[0-9a-f]{16}-01$", settings.traceparent)

    # Verify computed fields
    parts = settings.traceparent.split("-")
    assert settings.trace_id == parts[1]
    assert settings.span_id == parts[2]


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
    # Arrange & Act
    settings = LoggingSettings()

    # Assert
    assert settings.log_level == "DEBUG"
    assert settings.otel_exporter_otlp_endpoint == "http://localhost:4317"
    assert (
        settings.traceparent
        == "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"
    )
    assert settings.trace_id == "0af7651916cd43dd8448eb211c80319c"
    assert settings.span_id == "b7ad6b7169203331"


@mock.patch.dict(
    os.environ,
    {
        "WM_TRACEPARENT": "00-windmilltraceid1234567890123456-windmillspanid12-01",
    },
    clear=True,
)
def test_settings_from_windmill_env():
    """Test that settings correctly fallback to WM_TRACEPARENT."""
    # Arrange & Act
    settings = LoggingSettings()

    # Assert
    assert (
        settings.traceparent == "00-windmilltraceid1234567890123456-windmillspanid12-01"
    )
    assert settings.trace_id == "windmilltraceid1234567890123456"
    assert settings.span_id == "windmillspanid12"


@mock.patch.dict(
    os.environ,
    {
        "TRACEPARENT": "00-envtraceid1234567890123456789012-envspanid1234567-01",
        "WM_TRACEPARENT": "00-windmilltraceid1234567890123456-windmillspanid12-01",
    },
    clear=True,
)
def test_settings_precedence_env_over_windmill():
    """Test that TRACEPARENT takes precedence over WM_TRACEPARENT."""
    # Arrange & Act
    settings = LoggingSettings()

    # Assert
    assert (
        settings.traceparent
        == "00-envtraceid1234567890123456789012-envspanid1234567-01"
    )
    assert settings.trace_id == "envtraceid1234567890123456789012"
    assert settings.span_id == "envspanid1234567"


def test_is_windmill_env():
    # Arrange, Act, Assert
    settings = LoggingSettings(windmill_token="t", windmill_workspace="w")
    assert settings.is_windmill_env is True

    settings = LoggingSettings(windmill_token="t", windmill_workspace=None)
    assert settings.is_windmill_env is False

    settings = LoggingSettings(windmill_token=None, windmill_workspace="w")
    assert settings.is_windmill_env is False

    settings = LoggingSettings(windmill_token=None, windmill_workspace=None)
    assert settings.is_windmill_env is False


def test_vendor_defaults():
    # Arrange & Act
    settings = LoggingSettings()

    # Assert
    assert settings.posthog_host == "https://us.i.posthog.com"
    assert settings.langfuse_host == "https://cloud.langfuse.com"
    assert settings.sentry_dsn is None


def test_generate_traceparent():
    """Test generate_traceparent generates unique w3c traces."""
    # Arrange & Act
    tp1 = generate_traceparent()
    tp2 = generate_traceparent()

    # Assert
    assert re.match(r"^00-[0-9a-f]{32}-[0-9a-f]{16}-01$", tp1)
    assert re.match(r"^00-[0-9a-f]{32}-[0-9a-f]{16}-01$", tp2)
    assert tp1 != tp2


def test_malformed_traceparent_fails():
    """Test that setting a malformed traceparent that doesn't split to 4 parts raises an exception on computed access."""
    # Arrange & Act
    settings = LoggingSettings(traceparent="malformed")

    # Assert
    with pytest.raises(IndexError):
        _ = settings.trace_id

    with pytest.raises(IndexError):
        _ = settings.span_id
