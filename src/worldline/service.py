# src/worldline/service.py
import logging
import sys
from typing import Any, Dict, List, Optional, Tuple

import structlog
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from structlog.dev import (
    ConsoleRenderer,
    RichTracebackFormatter,
)

from worldline.config import settings


_WORLDLINE_CONFIGURED: bool = False


def setup(settings_override: Optional[Any] = None) -> None:
    """
    Orchestrates the setup of all Worldline integrations (Sentry, PostHog, Langfuse, Structlog).
    """
    global _WORLDLINE_CONFIGURED
    if _WORLDLINE_CONFIGURED:
        return

    current_settings = settings_override if settings_override else settings

    # 1. Sentry Setup
    if current_settings.sentry_dsn:
        import sentry_sdk

        sentry_sdk.init(dsn=current_settings.sentry_dsn)

    # 2. PostHog Setup
    if current_settings.posthog_api_key:
        import posthog

        posthog.project_api_key = current_settings.posthog_api_key
        posthog.host = current_settings.posthog_host

    # 3. Langfuse Setup
    if current_settings.langfuse_public_key:
        import langfuse

        langfuse.Langfuse(
            public_key=current_settings.langfuse_public_key,
            secret_key=current_settings.langfuse_secret_key,
            host=current_settings.langfuse_host or current_settings.langfuse_base_url,
        )

    # 4. Structlog Setup
    from worldline.integrations.structlog import setup_structlog

    setup_structlog(current_settings)

    _WORLDLINE_CONFIGURED = True


def remove_otel_context(
    logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Removes trace_id and span_id from the event dictionary.
    Used for console and rich formatters to prevent polluting terminal output.
    """
    event_dict = event_dict.copy()
    event_dict.pop("trace_id", None)
    event_dict.pop("span_id", None)
    return event_dict


def get_console_format() -> Tuple[List[Any], List[logging.Handler]]:
    """
    Returns processors and handlers for the structlog console format.
    Uses structlog.dev.ConsoleRenderer with RichTracebackFormatter for
    beautiful terminal output and traceback rendering.
    """
    console_renderer = ConsoleRenderer(
        colors=True,
        pad_event_to=40,
        sort_keys=False,
        exception_formatter=RichTracebackFormatter(
            show_locals=True, width=110, color_system="truecolor"
        ),
    )

    processors = [
        remove_otel_context,
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        console_renderer,
    ]

    handler = logging.StreamHandler(sys.stdout)

    return processors, [handler]


def add_otel_context(
    logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Injects OpenTelemetry trace_id and span_id into the log record.
    Falls back to the settings trace_id and span_id if no active OTel span is found.
    """
    # 1. Try to get it from the active OTel span
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        ctx = span.get_span_context()
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    else:
        # 2. Fallback to the context stored in settings
        event_dict["trace_id"] = settings.trace_id
        event_dict["span_id"] = settings.span_id

    return event_dict


def setup_otel_provider(
    settings_override: Optional[Any] = None,
) -> Optional[LoggerProvider]:
    """
    Initializes the OpenTelemetry LoggerProvider and TracerProvider with an OTLP exporter if configured.
    """
    current_settings = settings_override if settings_override else settings

    if not current_settings.is_windmill_env:
        return None

    logger_provider = LoggerProvider()
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry import trace as otel_trace

    tracer_provider = TracerProvider()

    headers = {"Authorization": f"Bearer {current_settings.windmill_token}"}

    log_endpoint = (
        f"{current_settings.windmill_base_url}/api/w/{current_settings.windmill_workspace}/tracing/v1/logs"
        if current_settings.windmill_base_url
        else current_settings.otel_exporter_otlp_logs_endpoint
    )
    trace_endpoint = (
        f"{current_settings.windmill_base_url}/api/w/{current_settings.windmill_workspace}/tracing/v1/traces"
        if current_settings.windmill_base_url
        else current_settings.otel_exporter_otlp_endpoint
    )

    log_exporter = OTLPLogExporter(endpoint=log_endpoint, headers=headers)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

    span_exporter = OTLPSpanExporter(endpoint=trace_endpoint, headers=headers)
    tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))

    set_logger_provider(logger_provider)
    otel_trace.set_tracer_provider(tracer_provider)

    return logger_provider
