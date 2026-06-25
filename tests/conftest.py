import os
import pytest
import structlog
from unittest import mock

from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk._logs.export import InMemoryLogExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import SimpleLogRecordProcessor


@pytest.fixture(autouse=True)
def clean_structlog():
    """Ensures structlog and logging defaults are reset before and after each test."""
    import logging

    structlog.reset_defaults()
    logging.getLogger().handlers.clear()
    yield
    structlog.reset_defaults()
    logging.getLogger().handlers.clear()


@pytest.fixture(autouse=True)
def env_reset():
    """Clears and restores environment variables to isolate tests."""
    old_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(old_env)


@pytest.fixture
def in_memory_otel_exporters():
    """
    Provides InMemoryLogExporter and InMemorySpanExporter to verify OpenTelemetry output
    without using mock.patch on the exporter classes.
    """
    span_exporter = InMemorySpanExporter()
    log_exporter = InMemoryLogExporter()

    logger_provider = LoggerProvider()
    logger_provider.add_log_record_processor(SimpleLogRecordProcessor(log_exporter))

    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))

    # Mock only the exporters. Let the real BatchProcessors use our InMemory exporters
    with (
        mock.patch("lume.service.OTLPLogExporter", return_value=log_exporter),
        mock.patch(
            "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter",
            return_value=span_exporter,
        ),
    ):
        yield {"log_exporter": log_exporter, "span_exporter": span_exporter}
