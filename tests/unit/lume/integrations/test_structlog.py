import logging
from io import StringIO
from unittest import mock

import pytest

from lume.integrations import structlog as lume_structlog


@pytest.fixture(autouse=True)
def reset_structlog_state():
    """Reset the module-level state before and after each test."""
    lume_structlog._LUME_CONFIGURED = False
    lume_structlog.reset_defaults()
    logging.getLogger().handlers.clear()
    yield
    lume_structlog._LUME_CONFIGURED = False
    lume_structlog.reset_defaults()
    logging.getLogger().handlers.clear()


@mock.patch("lume.integrations.structlog._original_structlog.configure", spec=True)
@mock.patch("lume.service.setup_otel_provider", spec=True)
def test_auto_initialization(mock_setup_otel, mock_configure):
    """Assert that calling get_logger implicitly configures the system."""
    mock_setup_otel.return_value = None

    # Initially not configured
    assert not lume_structlog._LUME_CONFIGURED

    # Act
    lume_structlog.get_logger()

    # Assert
    assert lume_structlog._LUME_CONFIGURED
    mock_configure.assert_called_once()


@mock.patch("lume.integrations.structlog._setup")
def test_idempotency(mock_setup):
    """Assert that get_logger only runs _setup once."""

    # We must patch get_logger directly to not actually call the setup if it was real,
    # wait, we're mocking _setup itself.
    # The first call will run the real check which is `if not _LUME_CONFIGURED: _setup()`
    # but _LUME_CONFIGURED will remain False because we mocked _setup!
    # So we need to have a side effect that sets _LUME_CONFIGURED to True.
    def mock_setup_side_effect(*args, **kwargs):
        lume_structlog._LUME_CONFIGURED = True

    mock_setup.side_effect = mock_setup_side_effect

    # Act
    lume_structlog.get_logger()
    lume_structlog.get_logger()

    # Assert
    mock_setup.assert_called_once()


def test_additive_configuration():
    """Assert that custom configure() intelligently merges processors."""

    def my_processor(logger, name, event_dict):
        event_dict["custom"] = "value"
        return event_dict

    # Trigger initialization and initial config
    lume_structlog.get_logger()

    # Store processors from first run
    initial_config = lume_structlog.get_config()
    initial_processors_len = len(initial_config["processors"])

    # Act
    lume_structlog.configure(processors=[my_processor])

    # Assert
    new_config = lume_structlog.get_config()
    assert len(new_config["processors"]) == initial_processors_len + 1
    # Check that custom processor is placed before the final formatter
    assert new_config["processors"][-2] == my_processor


def test_proxy_validation():
    """Assert that proxy attributes point to the original structlog counterparts."""
    import structlog

    assert lume_structlog.stdlib is structlog.stdlib
    assert lume_structlog.processors is structlog.processors
    assert lume_structlog.PrintLogger is structlog.PrintLogger


def test_dynamic_attribute():
    """Assert that non-explicitly imported attribute routes via __getattr__."""
    import structlog

    # make_filtering_bound_logger is in structlog but not explicitly exported in our __all__
    assert (
        lume_structlog.make_filtering_bound_logger
        is structlog.make_filtering_bound_logger
    )

    # Also test an actually missing attribute
    with pytest.raises(AttributeError):
        lume_structlog.does_not_exist


def test_standard_logging_capture():
    """Integration test to verify standard logging uses structlog format."""
    from rich.console import Console

    out = StringIO()

    # Trigger auto-setup
    lume_structlog.get_logger("test_capture")

    # Redirect console output for rich handler
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        from rich.logging import RichHandler

        if isinstance(handler, RichHandler):
            handler.console = Console(file=out, color_system=None)

    # Act
    std_logger = logging.getLogger("test_capture")
    std_logger.info("This is a standard log message")

    # Assert
    output_str = out.getvalue()
    assert "This is a standard log message" in output_str
    assert "test_capture" in output_str
