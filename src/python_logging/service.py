# src/python_logging/service.py
import logging
import sys
from typing import Any, List, Tuple

import structlog
from rich.logging import RichHandler


def get_console_renderer_format() -> Tuple[List[Any], List[logging.Handler]]:
    """
    Returns processors and handlers for the ConsoleRenderer format.
    Uses a colorized console renderer optimized for servers and workers.
    """
    processors = [
        structlog.dev.ConsoleRenderer(colors=True),
    ]
    
    handler = logging.StreamHandler(sys.stdout)
    
    return processors, [handler]


def get_rich_format() -> Tuple[List[Any], List[logging.Handler]]:
    """
    Returns processors and handlers for the rich format.
    Uses RichHandler for beautiful terminal output optimized for CLI apps.
    """
    # For RichHandler, we don't want structlog to format the final string,
    # we want it to pass the event dict to standard logging, which RichHandler intercepts.
    processors = [
        structlog.stdlib.render_to_log_kwargs,
    ]
    
    handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=True,
        show_level=True,
        show_path=False,
    )
    
    return processors, [handler]
