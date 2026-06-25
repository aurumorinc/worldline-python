# src/lume/service.py
import logging
from typing import Any, Dict, List, Optional, Tuple

import structlog
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from rich.logging import RichHandler

from lume.config import settings


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


def rich_renderer(
    logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
) -> str:
    """
    Renders structured kwargs to a formatted string using rich markup.
    """
    event = event_dict.pop("event", "")

    parts = [str(event)]
    for key, value in event_dict.items():
        parts.append(f"[dim]{key}=[/dim][cyan]{value}[/cyan]")

    return " ".join(parts)


def get_console_format() -> Tuple[List[Any], List[logging.Handler]]:
    """
    Returns processors and handlers for the rich console format.
    Uses RichHandler for beautiful terminal output optimized for CLI apps.
    """
    processors = [
        remove_otel_context,
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        rich_renderer,
    ]

    handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=True,
        show_level=True,
        show_path=False,
    )

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
