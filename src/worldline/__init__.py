# src/worldline/__init__.py
__version__ = "2.0.1"

import os
import sys

# Auto-instrumentation execution block
if not getattr(sys, "_WORLDLINE_INITIALIZED", False):
    sys._WORLDLINE_INITIALIZED = True

    if os.environ.get("WORLDLINE_DISABLE_AUTO_INSTRUMENTATION", "").lower() != "true":
        try:
            from worldline.service import setup

            setup()
        except Exception as e:
            sys.stderr.write(f"Worldline auto-instrumentation failed: {e}\n")

__all__ = ["__version__"]
