# python-logging

Org-level Python logging package providing structured, environment-agnostic logging with decoupled transports, OpenTelemetry, and Windmill integrations. Built on top of `structlog`, `rich`, and `opentelemetry`.

## Features

- **Structured Logging**: Powered by `structlog` for consistent, machine-readable logs.
- **Environment-Agnostic**: The logging package does not care about the deployment environment (`dev`, `prod`, etc.). It only cares about the requested `STDOUT_FORMAT` and active transports.
- **Decoupled Transports**: 
  - **Terminal Transport (stdout)**: Always active. Formatted according to `STDOUT_FORMAT`.
  - **OTLP Transport (Network)**: Active if OpenTelemetry endpoints are configured.
- **OpenTelemetry Integration**: Automatically injects `trace_id` and `span_id` into log records and supports exporting logs via OTLP.
- **Windmill Integration**: Extracts trace context from the `TRACEPARENT` environment variable as a fallback.
- **Configuration via Env Vars**: Easy configuration using `pydantic-settings`.

## Installation

You can install this package directly from the GitHub repository using `pip`:

```bash
pip install git+https://github.com/aurumorinc/python-logging.git
```

## Configuration

Configuration is handled via environment variables (or a `.env` file) using `pydantic-settings`.

| Environment Variable | Default | Description |
| :--- | :--- | :--- |
| `LOG_LEVEL` | `INFO` | The logging level (e.g., `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). |
| `STDOUT_FORMAT` | `ConsoleRenderer` | The format for the stdout transport. Must be one of: `ConsoleRenderer`, `rich`. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `None` | The OTLP endpoint for exporting logs (and other telemetry). |
| `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT` | `None` | The specific OTLP endpoint for exporting logs. |
| `TRACEPARENT` | `None` | W3C Trace Context string, used by Windmill for distributed tracing. |

## Usage

**CRITICAL RULE:** You must call `setup_logging()` **exactly once** at the very entry point of your application (e.g., in your `main.py`, `app.py`, or CLI entry script). Because it configures the global logging state, you do *not* need to call it in every file. In all other files, simply import and use `get_logger(__name__)`.

### Integrating with Project Settings (Pydantic)

If your project already uses `pydantic-settings`, you can easily merge the logging configuration into your main settings class by inheriting from `LoggingSettings`. This allows you to validate all environment variables (both app-specific and logging-specific) in one place.

```python
from pydantic_settings import BaseSettings
from python_logging.config import LoggingSettings
from python_logging.main import setup_logging

# Inherit from LoggingSettings to include logging configuration
class AppSettings(LoggingSettings, BaseSettings):
    app_name: str = "my-awesome-app"
    database_url: str

# Instantiate your combined settings
settings = AppSettings()

# Pass the combined settings to setup_logging
setup_logging(settings)
```

### Basic Usage

**In your entry point file (e.g., `main.py`):**
```python
from python_logging.main import setup_logging

# 1. Initialize global logging state (call this exactly once)
setup_logging()
```

**In any other file in your project:**
```python
from python_logging.main import get_logger

# 2. Get a logger instance for this module
logger = get_logger(__name__)

# 3. Log messages with structured data
logger.info("user_logged_in", user_id=123, ip_address="192.168.1.1")

try:
    1 / 0
except ZeroDivisionError:
    logger.exception("calculation_failed", operation="division")
```

### Context Variables

You can bind context variables to a logger so they are included in all subsequent log calls from that logger.

```python
from python_logging.main import get_logger

logger = get_logger(__name__).bind(request_id="req-abc-123")

logger.info("processing_request") 
# Includes: request_id="req-abc-123"

logger.info("request_completed", status=200) 
# Includes: request_id="req-abc-123", status=200
```

### OpenTelemetry Integration

If you are using OpenTelemetry for distributed tracing, `python-logging` will automatically extract the active `trace_id` and `span_id` and inject them into your log records.

If you configure `OTEL_EXPORTER_OTLP_ENDPOINT` or `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT`, logs will also be exported to your OTLP collector automatically.

```python
from opentelemetry import trace
from python_logging.main import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("my_operation"):
    # This log will automatically include trace_id and span_id
    logger.info("operation_started")
```

### Windmill Integration

When running inside Windmill, OpenTelemetry spans might not be actively managed in the Python process, but Windmill passes the trace context via the `TRACEPARENT` environment variable. `python-logging` automatically detects this and injects the `trace_id` and `span_id` into your logs.

```bash
export TRACEPARENT="00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"
```

```python
from python_logging.main import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

# This log will include trace_id="0af7651916cd43dd8448eb211c80319c" and span_id="b7ad6b7169203331"
logger.info("running_in_windmill")
```

## Stdout Formats & Log Output Examples

The output format for the terminal transport is controlled by the `STDOUT_FORMAT` variable.

### ConsoleRenderer (`STDOUT_FORMAT=ConsoleRenderer`)

Optimized for servers (like FastAPI) and workers (like Windmill). Uses `structlog.dev.ConsoleRenderer` to provide colorized, easy-to-read output with clear key-value pairs.

**Configuration:**
```bash
export STDOUT_FORMAT=ConsoleRenderer
export LOG_LEVEL=DEBUG
```

**Code:**
```python
logger.debug("database_query", table="users", duration_ms=15.2)
logger.info("user_created", user_id=42)
```

**Output Example:**
```text
2026-05-20T14:32:10.123456Z [debug    ] database_query                 duration_ms=15.2 table=users
2026-05-20T14:32:10.124567Z [info     ] user_created                   user_id=42
```
*(Note: The actual output will be colorized in your terminal)*

### Rich (`STDOUT_FORMAT=rich`)

Optimized for command-line interfaces (CLI apps like Typer) where you want beautiful, rich formatting for the end-user. Uses `rich.logging.RichHandler`.

**Configuration:**
```bash
export STDOUT_FORMAT=rich
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
*(Note: The actual output will be beautifully formatted and colorized by `rich`, with aligned timestamps and levels)*

## Development

To set up the project for development:

1. Ensure you have Python 3.9+ installed.
2. Install dependencies (using `pdm`, `hatch`, or `pip`):
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests:
   ```bash
   pytest
   ```
