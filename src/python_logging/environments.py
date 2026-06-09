# src/python_logging/environments.py
import logging
import sys
from typing import Any, List, Tuple

import structlog
from rich.logging import RichHandler


def get_dev_config() -> Tuple[List[Any], List[logging.Handler]]:
    """
    Returns processors and handlers for the development environment.
    Uses a colorized console renderer.
    """
    processors = [
        structlog.dev.ConsoleRenderer(colors=True),
    ]
    
    handler = logging.StreamHandler(sys.stdout)
    
    return processors, [handler]


def get_prod_config() -> Tuple[List[Any], List[logging.Handler]]:
    """
    Returns processors and handlers for the production environment.
    Uses a JSON renderer for log aggregators.
    """
    processors = [
        structlog.processors.JSONRenderer(),
    ]
    
    handler = logging.StreamHandler(sys.stdout)
    
    return processors, [handler]


def get_cli_config() -> Tuple[List[Any], List[logging.Handler]]:
    """
    Returns processors and handlers for the CLI environment.
    Uses RichHandler for beautiful terminal output.
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
