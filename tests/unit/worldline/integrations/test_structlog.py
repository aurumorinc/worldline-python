import logging
from unittest import mock

import pytest
import structlog

from worldline.integrations.structlog import setup_structlog


@pytest.fixture(autouse=True)
def reset_structlog_state():
    """Reset the module-level state before and after each test."""
    structlog.reset_defaults()
    logging.getLogger().handlers.clear()
    yield
    structlog.reset_defaults()
    logging.getLogger().handlers.clear()


@mock.patch("structlog.configure", spec=True)
@mock.patch("worldline.service.setup_otel_provider", spec=True)
def test_setup_structlog(mock_setup_otel, mock_configure):
    """Assert that setup_structlog correctly configures structlog and standard logging."""
    mock_setup_otel.return_value = None

    # Act
    setup_structlog()

    # Assert
    mock_configure.assert_called_once()
    assert len(logging.getLogger().handlers) > 0


@mock.patch("worldline.service.setup_otel_provider", spec=True)
def test_setup_structlog_with_otel(mock_setup_otel):
    """Assert that setup_structlog correctly sets up OTel handler if provider exists."""
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from worldline.config import WorldlineSettings

    mock_provider = LoggerProvider()
    mock_setup_otel.return_value = mock_provider

    settings = WorldlineSettings()

    # Act
    setup_structlog(settings)

    # Assert
    handlers = logging.getLogger().handlers
    assert any(isinstance(h, LoggingHandler) for h in handlers)
