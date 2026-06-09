# tests/unit/python_logging/test_main.py
import logging
from unittest import mock

from python_logging.config import LoggingSettings, StdoutFormat
from python_logging.main import setup_logging


@mock.patch("python_logging.main.structlog.configure")
@mock.patch("python_logging.main.setup_otel_provider")
def test_setup_logging_console_renderer(mock_setup_otel, mock_configure):
    """Test setup_logging with ConsoleRenderer format."""
    mock_setup_otel.return_value = None
    settings = LoggingSettings(stdout_format=StdoutFormat.CONSOLE_RENDERER)
    
    setup_logging(settings)
    
    # Verify structlog was configured
    mock_configure.assert_called_once()
    
    # Verify root logger has one handler (StreamHandler)
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0], logging.StreamHandler)


@mock.patch("python_logging.main.structlog.configure")
@mock.patch("python_logging.main.setup_otel_provider")
def test_setup_logging_rich(mock_setup_otel, mock_configure):
    """Test setup_logging with rich format."""
    mock_setup_otel.return_value = None
    settings = LoggingSettings(stdout_format=StdoutFormat.RICH)
    
    setup_logging(settings)
    
    # Verify structlog was configured
    mock_configure.assert_called_once()
    
    # Verify root logger has one handler (RichHandler)
    from rich.logging import RichHandler
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0], RichHandler)


@mock.patch("python_logging.main.structlog.configure")
@mock.patch("python_logging.main.setup_otel_provider")
def test_setup_logging_with_otel(mock_setup_otel, mock_configure):
    """Test setup_logging adds OTLP handler when provider is available."""
    # Mock a dummy provider
    mock_provider = mock.Mock()
    mock_setup_otel.return_value = mock_provider
    
    settings = LoggingSettings(stdout_format=StdoutFormat.CONSOLE_RENDERER)
    setup_logging(settings)
    
    # Verify root logger has two handlers (StreamHandler + LoggingHandler for OTLP)
    from opentelemetry.sdk._logs import LoggingHandler
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) == 2
    
    handler_types = [type(h) for h in root_logger.handlers]
    assert logging.StreamHandler in handler_types
    assert LoggingHandler in handler_types
