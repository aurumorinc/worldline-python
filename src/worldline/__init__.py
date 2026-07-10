# src/worldline/__init__.py
__version__ = "2.0.1"

from worldline import config
from worldline import integrations
from worldline import service

from worldline.config import (WorldlineSettings, generate_traceparent,
                              resolve_traceparent, settings,)
from worldline.integrations import (BoundLogger, DropEvent, PrintLogger,
                                    ReturnLogger, WriteLogger, configure,
                                    configure_once, contextvars, dev,
                                    getLogger, get_config, get_context,
                                    get_logger, get_windmill_traceparent,
                                    is_configured, langfuse, observe, posthog,
                                    processors, reset_defaults, sentry,
                                    sentry_sdk, stdlib, structlog, testing,
                                    threadlocal, windmill, wrap_logger,)
from worldline.service import (add_otel_context, get_console_format,
                               remove_otel_context, setup_otel_provider,)

__all__ = ['BoundLogger', 'DropEvent', 'PrintLogger', 'ReturnLogger',
           'WorldlineSettings', 'WriteLogger', 'add_otel_context', 'config',
           'configure', 'configure_once', 'contextvars', 'dev',
           'generate_traceparent', 'getLogger', 'get_config',
           'get_console_format', 'get_context', 'get_logger',
           'get_windmill_traceparent', 'integrations', 'is_configured',
           'langfuse', 'observe', 'posthog', 'processors',
           'remove_otel_context', 'reset_defaults', 'resolve_traceparent',
           'sentry', 'sentry_sdk', 'service', 'settings',
           'setup_otel_provider', 'stdlib', 'structlog', 'testing',
           'threadlocal', 'windmill', 'wrap_logger']

# Eagerly initialize all telemetry integrations upon package import
structlog._setup()
