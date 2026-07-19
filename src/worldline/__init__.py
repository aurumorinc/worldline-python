# src/worldline/__init__.py
__version__ = "2.0.0"

import os
import sys

# Auto-instrumentation execution block
if not getattr(sys, "_WORLDLINE_INITIALIZED", False):
    setattr(sys, "_WORLDLINE_INITIALIZED", True)

    if os.environ.get("WORLDLINE_DISABLE_AUTO_INSTRUMENTATION", "").lower() != "true":
        try:
            from worldline.service import setup

            setup()
        except Exception as e:
            sys.stderr.write(f"Worldline auto-instrumentation failed: {e}\n")

# <AUTOGEN_INIT>
from worldline import config
from worldline import integrations
from worldline import service

from worldline.config import (
    WorldlineSettings,
    generate_traceparent,
    resolve_traceparent,
    settings,
)
from worldline.integrations import (
    get_windmill_traceparent,
    setup_structlog,
    structlog,
    windmill,
)
from worldline.service import (
    add_otel_context,
    get_console_format,
    remove_otel_context,
    setup,
    setup_otel_provider,
)

__all__ = [
    "WorldlineSettings",
    "add_otel_context",
    "config",
    "generate_traceparent",
    "get_console_format",
    "get_windmill_traceparent",
    "integrations",
    "remove_otel_context",
    "resolve_traceparent",
    "service",
    "settings",
    "setup",
    "setup_otel_provider",
    "setup_structlog",
    "structlog",
    "windmill",
]
# </AUTOGEN_INIT>
