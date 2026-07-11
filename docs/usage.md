# Usage Guide

**CRITICAL RULE:** Telemetry and logging are eagerly initialized on Python startup via zero-touch auto-instrumentation (using a `.pth` file). By simply installing `worldline`, the global observability state is configured automatically via environment variables before your application code even runs.

If you ever need to disable this behavior (e.g., for certain testing environments), set the environment variable:
`WORLDLINE_DISABLE_AUTO_INSTRUMENTATION=true`

## Basic Logging Usage

Because `worldline` modifies the global `structlog` state at initialization, you use the standard `structlog` package directly throughout your codebase.

```python
import structlog

# 1. Get a logger instance for this module
logger = structlog.get_logger(__name__)

# 2. Log messages with structured data
logger.info("user_logged_in", user_id=123, ip_address="192.168.1.1")

try:
    1 / 0
except ZeroDivisionError:
    logger.exception("calculation_failed", operation="division")
```

## Context Variables

You can bind context variables to a logger so they are included in all subsequent log calls from that logger.

```python
import structlog

logger = structlog.get_logger(__name__).bind(request_id="req-abc-123")

logger.info("processing_request") 
# Includes: request_id="req-abc-123"

logger.info("request_completed", status=200) 
# Includes: request_id="req-abc-123", status=200
```

## Vendor Integrations

`worldline` automatically initializes Sentry, PostHog, and Langfuse globally if their respective configuration variables are present in the environment. You simply import the standard vendor libraries directly in your consumer application.

```python
import sentry_sdk
import posthog
from langfuse.decorators import observe

# Sentry
sentry_sdk.capture_message("Something went wrong")

# PostHog
posthog.capture("user_123", "event_name", properties={"key": "value"})

# Langfuse (via decorator natively from the package)
@observe(as_type="generation")
def my_llm_call(prompt):
    return "LLM Response"
```

## OpenTelemetry & Windmill Integration

If you configure `WINDMILL_TOKEN` and `WINDMILL_WORKSPACE`, logs and traces will automatically be exported to the Windmill platform.

`worldline` will also automatically extract the active `trace_id` and `span_id` and inject them into your log records. When running inside Windmill, it automatically extracts tracing contexts from the environment.

## Terminal Output

Worldline uses `rich.logging.RichHandler` for beautiful, structured formatting in the terminal.

**Configuration:**
```bash
export LOG_LEVEL=INFO
```

**Code:**
```python
logger.info("Starting data synchronization...")
logger.warning("Rate limit approaching", current=95, max=100)
```

**Output Example:**
```text
[14:38:01] INFO     Starting data synchronization...
           WARNING  Rate limit approaching                             current=95 max=100
```
*(Note: The actual output will be beautifully formatted and colorized by `rich`, with aligned timestamps, levels, and structured key-value pairs)*
