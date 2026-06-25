# tests/unit/lume/test_service.py
import logging
from unittest import mock


from lume.service import (
    add_otel_context,
    remove_otel_context,
    setup_otel_provider,
)


def test_add_otel_context_with_active_span():
    # Arrange
    from opentelemetry.sdk.trace import TracerProvider

    provider = TracerProvider()
    tracer = provider.get_tracer(__name__)

    with tracer.start_as_current_span("test_span") as span:
        ctx = span.get_span_context()
        event_dict = {}

        with mock.patch("lume.service.trace.get_current_span", return_value=span):
            # Act
            result = add_otel_context(logging.getLogger(), "info", event_dict)

            # Assert
            assert result["trace_id"] == format(ctx.trace_id, "032x")
            assert result["span_id"] == format(ctx.span_id, "016x")


@mock.patch("lume.service.settings")
def test_add_otel_context_fallback_to_settings(mock_settings):
    # Arrange
    mock_settings.trace_id = "settings_trace"
    mock_settings.span_id = "settings_span"

    event_dict = {}

    # Act
    result = add_otel_context(logging.getLogger(), "info", event_dict)

    # Assert
    assert result["trace_id"] == "settings_trace"
    assert result["span_id"] == "settings_span"


@mock.patch("lume.service.settings")
def test_add_otel_context_empty_event_dict(mock_settings):
    """Test adding context to an empty dict still adds trace_id and span_id."""
    # Arrange
    mock_settings.trace_id = "1"
    mock_settings.span_id = "2"
    event_dict = {}

    # Act
    result = add_otel_context(logging.getLogger(), "info", event_dict)

    # Assert
    assert result == {"trace_id": "1", "span_id": "2"}


@mock.patch("lume.service.settings")
def test_setup_otel_provider_no_endpoint(mock_settings):
    # Arrange
    mock_settings.is_windmill_env = False

    # Act
    provider = setup_otel_provider()

    # Assert
    assert provider is None


@mock.patch("lume.service.settings")
def test_setup_otel_provider_with_endpoint(mock_settings):
    # Arrange
    mock_settings.is_windmill_env = True
    mock_settings.windmill_token = "dummy_token"
    mock_settings.windmill_base_url = "https://app.windmill.dev"
    mock_settings.windmill_workspace = "my_workspace"

    # Act
    provider = setup_otel_provider()

    # Assert
    assert provider is not None


def test_remove_otel_context():
    # Arrange
    event_dict = {
        "event": "test message",
        "trace_id": "test_trace_id",
        "span_id": "test_span_id",
        "other_key": "value",
    }

    # Act
    result = remove_otel_context(logging.getLogger(), "info", event_dict)

    # Assert
    # Verify the keys were removed in the result
    assert "trace_id" not in result
    assert "span_id" not in result
    assert result["event"] == "test message"
    assert result["other_key"] == "value"

    # Verify the original dictionary was NOT mutated
    assert "trace_id" in event_dict
    assert "span_id" in event_dict


def test_remove_otel_context_missing_keys():
    """Test removing context when keys are not present."""
    # Arrange
    event_dict = {"event": "test message"}

    # Act
    result = remove_otel_context(logging.getLogger(), "info", event_dict)

    # Assert
    assert result == {"event": "test message"}
    assert result is not event_dict  # Still returns a copy
