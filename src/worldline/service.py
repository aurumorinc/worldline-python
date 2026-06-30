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
    Column,
    ConsoleRenderer,
    KeyValueColumnFormatter,
    LogLevelColumnFormatter,
    RichTracebackFormatter,
)

from worldline.config import settings


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
    styles = ConsoleRenderer.get_default_column_styles(colors=True)

    console_renderer = ConsoleRenderer(
        columns=[
            Column(
                "timestamp",
                formatter=KeyValueColumnFormatter(
                    key_style=None,
                    value_style=styles.timestamp,
                    reset_style=styles.reset,
                    value_repr=str,
                ),
            ),
            Column(
                "level",
                formatter=LogLevelColumnFormatter(
                    level_styles=ConsoleRenderer.get_default_level_styles(colors=True),
                    reset_style=styles.reset,
                ),
            ),
            Column(
                "event",
                formatter=KeyValueColumnFormatter(
                    key_style=None,
                    value_style=styles.bright,
                    reset_style=styles.reset,
                    value_repr=str,
                ),
            ),
            Column(
                "",
                formatter=KeyValueColumnFormatter(
                    key_style=styles.kv_key,
                    value_style=styles.kv_value,
                    reset_style=styles.reset,
                    value_repr=repr,
                ),
            ),
        ],
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
