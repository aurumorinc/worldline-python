import logging
from unittest import mock


from python_logging.service import add_otel_context, setup_otel_provider


def test_add_otel_context_with_active_span():
    from opentelemetry.sdk.trace import TracerProvider

    provider = TracerProvider()
    tracer = provider.get_tracer(__name__)

    with tracer.start_as_current_span("test_span") as span:
        # We need to set the current span in the context manually for the test
        # or use the tracer properly. start_as_current_span does this.
        ctx = span.get_span_context()
        event_dict = {}

        # Mock trace.get_current_span to return our span since the global provider isn't set
        with mock.patch(
            "python_logging.service.trace.get_current_span", return_value=span
        ):
            result = add_otel_context(logging.getLogger(), "info", event_dict)

            assert result["trace_id"] == format(ctx.trace_id, "032x")
            assert result["span_id"] == format(ctx.span_id, "016x")


@mock.patch("python_logging.service.get_windmill_context")
def test_add_otel_context_fallback_to_windmill(mock_get_windmill_context):
    mock_get_windmill_context.return_value = {
        "trace_id": "windmill_trace",
        "span_id": "windmill_span",
    }

    event_dict = {}
    result = add_otel_context(logging.getLogger(), "info", event_dict)

    assert result["trace_id"] == "windmill_trace"
    assert result["span_id"] == "windmill_span"


@mock.patch("python_logging.service.settings")
def test_setup_otel_provider_no_endpoint(mock_settings):
    mock_settings.otel_exporter_otlp_endpoint = None
    mock_settings.otel_exporter_otlp_logs_endpoint = None
    provider = setup_otel_provider()
    assert provider is None


@mock.patch("python_logging.service.settings")
def test_setup_otel_provider_with_endpoint(mock_settings):
    mock_settings.otel_exporter_otlp_endpoint = "http://localhost:4317"
    mock_settings.otel_exporter_otlp_logs_endpoint = None
    provider = setup_otel_provider()
    assert provider is not None
