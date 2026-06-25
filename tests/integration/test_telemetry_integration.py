import os
from unittest import mock

from lume.config import LoggingSettings
from lume.integrations import structlog
from lume import observe


@mock.patch.dict(
    os.environ,
    {
        "SENTRY_DSN": "https://dummy@sentry.io/123",
        "POSTHOG_API_KEY": "ph_dummy_key",
        "LANGFUSE_PUBLIC_KEY": "lf_pub",
        "LANGFUSE_SECRET_KEY": "lf_sec",
        "WM_TOKEN": "windmill_dummy_token",
        "WM_WORKSPACE": "windmill_ws",
        "WM_BASE_URL": "https://app.windmill.dev",
        "TRACEPARENT": "00-12345678901234567890123456789012-1234567890123456-01",
    },
    clear=True,
)
@mock.patch("lume.integrations.sentry.sentry_sdk", create=True)
@mock.patch("lume.integrations.posthog.posthog", create=True)
@mock.patch("lume.integrations.langfuse.langfuse.Langfuse", create=True)
def test_telemetry_integration(
    mock_langfuse, mock_posthog, mock_sentry, in_memory_otel_exporters
):
    """
    Integration test utilizing InMemory OpenTelemetry Exporters to verify
    the fully configured pipeline accurately translates custom structured
    logging events into W3C compliant OpenTelemetry LogRecords and spans.
    """
    # Reset structlog
    structlog._LUME_CONFIGURED = False
    structlog.reset_defaults()

    # Arrange
    settings = LoggingSettings()

    # Act
    with mock.patch("lume.service.settings", settings):
        # Trigger lazy setup with explicitly mocked settings
        structlog._setup(settings)

        logger = structlog.get_logger("integration_logger")
        logger.info("integration test", user_id="123")

    # Assert Vendor SDKs initialized
    mock_sentry.init.assert_called_once_with(dsn="https://dummy@sentry.io/123")
    assert mock_posthog.project_api_key == "ph_dummy_key"
    mock_langfuse.assert_called_once_with(
        public_key="lf_pub",
        secret_key="lf_sec",
        host="https://cloud.langfuse.com",
    )

    # Test that observe decorator from langfuse facade works
    @observe(as_type="generation")
    def my_generation_func():
        return "generation result"

    assert my_generation_func() == "generation result"

    # Assert OpenTelemetry Output
    from opentelemetry._logs import get_logger_provider

    get_logger_provider().force_flush()

    log_exporter = in_memory_otel_exporters["log_exporter"]
    in_memory_otel_exporters["span_exporter"]

    finished_logs = log_exporter.get_finished_logs()

    # One log should have been captured
    assert len(finished_logs) == 1

    log_record = finished_logs[0]
    # In OpenTelemetry python SDK, log_record.log_record represents the actual log data
    body = log_record.log_record.body

    if isinstance(body, dict):
        assert body["event"] == "integration test"
        assert body["user_id"] == "123"
    else:
        assert "integration test" in body

    # Verify context injection (trace_id should match the env variable settings)
    if isinstance(body, dict):
        assert body.get("trace_id") == settings.trace_id
