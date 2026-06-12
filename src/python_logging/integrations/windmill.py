# src/python_logging/integrations/windmill.py
import os
from typing import Optional


def get_windmill_traceparent() -> Optional[str]:
    """
    Extracts the traceparent from the Windmill environment variable.

    Returns:
        The traceparent string if found, otherwise None.
    """
    return os.environ.get("WM_TRACEPARENT")
