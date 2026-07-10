# Worldline

Worldline is a unified observability and telemetry bootstrapper for Python. It provides structured, environment-agnostic logging alongside native vendor facades for Sentry, PostHog, Langfuse, and OpenTelemetry. Built on top of `structlog`, `rich`, and `opentelemetry`, Worldline allows you to configure your entire observability stack with a single function call while maintaining direct access to underlying native SDKs.

## Features

- **Zero-Config Bootstrapper**: Simply importing from `worldline` eagerly configures your entire telemetry stack (Logging, Sentry, PostHog, Langfuse, and OpenTelemetry) based on the presence of environment variables.
- **Submodule Vendor Re-export**: Access Sentry, PostHog, and Langfuse natively directly through `worldline` (e.g., `from worldline import sentry_sdk`). This preserves original typings and API surfaces while keeping dependency versions centralized in this package.
- **Structured Logging**: Powered by `structlog` for consistent, machine-readable logs.
- **Decoupled Transports**: 
  - **Terminal Transport (stdout)**: Always active, beautifully formatted with `rich`.
  - **Bifurcated OpenTelemetry (Network)**: OTLP exporters spin up *strictly* when running inside Windmill (detected via `WINDMILL_TOKEN` and `WINDMILL_WORKSPACE`), ensuring no idle exporters in local/dev environments.
- **Context Injection**: Automatically injects `trace_id` and `span_id` from OpenTelemetry into log records.
- **Configuration via Env Vars**: Easy configuration using `pydantic-settings`.

## Documentation

- [Configuration Guide](docs/configuration.md) - Learn how to configure vendors via environment variables and `pydantic-settings`.
- [Usage Guide](docs/usage.md) - See examples for structural logging, context variables, and native vendor facades.

## Installation

You can install this package directly from the GitHub repository using `pip`:

```bash
pip install git+https://github.com/aurumorinc/worldline-python.git
```

*(Note: While the repository is `worldline-python`, the importable package is `worldline`)*

## Quickstart

Telemetry and logging are eagerly initialized on package import. By simply importing from `worldline`, the global observability state is configured automatically.

```python
from worldline import structlog

# 1. Get a logger instance for this module
logger = structlog.get_logger(__name__)

# 2. Log messages with structured data
logger.info("user_logged_in", user_id=123, ip_address="192.168.1.1")
```

## Development

To set up the project for development:

1. Ensure you have Python 3.11+ installed.
2. Install dependencies (using `pdm`):
   ```bash
   pdm install
   ```
3. Run tests:
   ```bash
   pdm run pytest
   ```

## Release Process

This project uses [Release Please](https://github.com/googleapis/release-please) to automate versioning and changelog generation.

To trigger a release:
1. Merge your changes into the `main` branch using [Conventional Commits](https://www.conventionalcommits.org/) (e.g., `feat: add new feature`, `fix: resolve bug`).
2. Release Please will automatically create or update a Release PR.
3. When you are ready to release, merge the Release PR. This will tag the release and update the changelog.
