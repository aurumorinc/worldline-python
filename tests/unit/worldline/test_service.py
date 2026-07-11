# tests/unit/worldline/test_service.py
import logging
from unittest import mock


import worldline.service as service_module
from worldline.service import (
    add_otel_context,
    get_console_format,
    remove_otel_context,
    setup,
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

        with mock.patch("worldline.service.trace.get_current_span", return_value=span):
            # Act
            result = add_otel_context(logging.getLogger(), "info", event_dict)

            # Assert
            assert result["trace_id"] == format(ctx.trace_id, "032x")
            assert result["span_id"] == format(ctx.span_id, "016x")


@mock.patch("worldline.service.settings")
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


@mock.patch("worldline.service.settings")
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


@mock.patch("worldline.service.settings")
def test_setup_otel_provider_no_endpoint(mock_settings):
    # Arrange
    mock_settings.is_windmill_env = False

    # Act
    provider = setup_otel_provider()

    # Assert
    assert provider is None


@mock.patch("worldline.service.settings")
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


def test_get_console_format():
    """Test get_console_format returns the expected processors and handlers."""
    import sys
    import structlog

    processors, handlers = get_console_format()

    assert len(processors) == 3
    assert processors[0] == remove_otel_context
    assert processors[1] == structlog.stdlib.ProcessorFormatter.remove_processors_meta
    assert isinstance(processors[2], structlog.dev.ConsoleRenderer)

    assert len(handlers) == 1
    assert isinstance(handlers[0], logging.StreamHandler)
    assert handlers[0].stream is sys.stdout


@mock.patch.dict("os.environ", {}, clear=True)
@mock.patch("worldline.integrations.structlog.setup_structlog")
@mock.patch("langfuse.Langfuse")
@mock.patch("posthog.project_api_key", create=True)
@mock.patch("posthog.host", create=True)
@mock.patch("sentry_sdk.init", create=True)
def test_setup_orchestration(mock_sentry_init, mock_posthog_host, mock_posthog_api_key, mock_langfuse, mock_setup_structlog):
    """Test that setup() correctly orchestrates integrations based on settings."""
    from worldline.config import WorldlineSettings
    
    # Reset state
    service_module._WORLDLINE_CONFIGURED = False
    
    settings = WorldlineSettings(
        sentry_dsn="https://dummy@sentry.io/123",
        posthog_api_key="ph_key",
        posthog_host="ph_host",
        langfuse_public_key="lf_pub",
        langfuse_secret_key="lf_sec",
        langfuse_base_url="lf_host",
        langfuse_host="lf_host"
    )

    with mock.patch.dict("sys.modules", {"posthog": mock.MagicMock()}):
        import sys
        mock_posthog = sys.modules["posthog"]
        setup(settings)

        # Assert Sentry
        mock_sentry_init.assert_called_once_with(dsn="https://dummy@sentry.io/123")
        
        # Assert PostHog
        assert mock_posthog.project_api_key == "ph_key"
        assert mock_posthog.host == "ph_host"
        
        # Assert Langfuse
        mock_langfuse.assert_called_once_with(
            public_key="lf_pub",
            secret_key="lf_sec",
            host="lf_host"
        )
        
        # Assert Structlog
        mock_setup_structlog.assert_called_once_with(settings)
        
        # Assert state
        assert service_module._WORLDLINE_CONFIGURED is True


@mock.patch("worldline.integrations.structlog.setup_structlog")
def test_setup_idempotency(mock_setup_structlog):
    """Test that setup() is idempotent."""
    # Reset state
    service_module._WORLDLINE_CONFIGURED = False
    
    setup()
    setup()
    
    # Should only be called once
    mock_setup_structlog.assert_called_once()
