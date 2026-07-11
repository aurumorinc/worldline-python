import logging
from io import StringIO
from unittest import mock

import pytest
import structlog

from worldline.service import setup


@pytest.fixture(autouse=True)
def reset_state():
    """Reset the module-level state before and after each test."""
    import worldline.service as service_module
    
    service_module._WORLDLINE_CONFIGURED = False
    structlog.reset_defaults()
    logging.getLogger().handlers.clear()
    yield
    service_module._WORLDLINE_CONFIGURED = False
    structlog.reset_defaults()
    logging.getLogger().handlers.clear()


def test_standard_logging_capture():
    """Integration test to verify standard logging uses structlog format."""
    out = StringIO()

    # Trigger auto-setup
    setup()

    # Redirect console output for StreamHandler
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.stream = out

    # Act
    std_logger = logging.getLogger("test_capture")
    std_logger.info("This is a standard log message")

    # Assert
    output_str = out.getvalue()
    assert "This is a standard log message" in output_str
    assert "test_capture" in output_str


def test_setup_configures_otel(in_memory_otel_exporters):
    """Test that when configuring OTEL, OpenTelemetry records the logs."""
    from worldline.config import WorldlineSettings

    settings = WorldlineSettings(
        windmill_token="windmill_dummy_token",
        windmill_workspace="windmill_ws",
        traceparent="00-12345678901234567890123456789012-1234567890123456-01",
    )

    with mock.patch("worldline.service.settings", settings):
        setup(settings)

        logger = structlog.get_logger("integration_logger")
        logger.info("integration test", user_id="123")

    from opentelemetry._logs import get_logger_provider
    import typing
    from opentelemetry.sdk._logs import LoggerProvider

    provider = typing.cast(LoggerProvider, get_logger_provider())
    provider.force_flush()

    log_exporter = in_memory_otel_exporters["log_exporter"]

    finished_logs = log_exporter.get_finished_logs()
    assert len(finished_logs) == 1

    log_record = finished_logs[0]
    body = log_record.log_record.body

    if isinstance(body, dict):
        assert body["event"] == "integration test"
        assert body["user_id"] == "123"
        assert body.get("trace_id") == settings.trace_id
    else:
        assert "integration test" in body
