# tests/unit/python_logging/test_main.py
import logging
import sys
from io import StringIO
from unittest import mock

import structlog

from python_logging.config import LoggingSettings, StdoutFormat
from python_logging.main import get_logger, setup_logging


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


def test_console_renderer_output_is_clean():
    """
    Integration test to verify that the terminal output does NOT
    contain trace_id, span_id, _record, or _from_structlog keys.
    """
    structlog.reset_defaults()
    
    # We must patch sys.stdout for StreamHandler initialization
    out = StringIO()
    with mock.patch("sys.stdout", out):
        settings = LoggingSettings(stdout_format=StdoutFormat.CONSOLE_RENDERER)
        setup_logging(settings)

        logger = get_logger("test_clean")
        logger.info("This is a clean log message")
        
        output_str = out.getvalue()
        
        # Verify internal structural keys are not in the output
        assert "_record" not in output_str
        assert "_from_structlog" not in output_str
        assert "trace_id" not in output_str
        assert "span_id" not in output_str
        assert "This is a clean log message" in output_str
        
    structlog.reset_defaults()

