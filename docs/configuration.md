# Configuration

Worldline configuration is handled via environment variables (or a `.env` file) using `pydantic-settings`.

## Environment Variables

| Environment Variable | Default | Description |
| :--- | :--- | :--- |
| `LOG_LEVEL` | `INFO` | The logging level (e.g., `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). |
| `SENTRY_DSN` | `None` | The DSN for Sentry. If provided, Sentry will be automatically initialized. |
| `POSTHOG_API_KEY` | `None` | Project API Key for PostHog. If provided, PostHog will be automatically configured. |
| `POSTHOG_HOST` | `https://us.i.posthog.com` | Host URL for PostHog. |
| `LANGFUSE_PUBLIC_KEY` | `None` | Public Key for Langfuse. |
| `LANGFUSE_SECRET_KEY` | `None` | Secret Key for Langfuse. If both keys are provided, Langfuse is initialized. |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Host URL for Langfuse. |
| `WINDMILL_TOKEN` | `None` | Windmill Workspace Token. Required for Windmill OTEL. |
| `WINDMILL_WORKSPACE` | `None` | Windmill Workspace Name. Required for Windmill OTEL. |
| `WINDMILL_BASE_URL` | `None` | Base URL for Windmill, used for resolving OTEL endpoints. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `None` | Fallback OTLP endpoint for exporting traces. |
| `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT`| `None` | Fallback specific OTLP endpoint for exporting logs. |

## Integrating with Project Settings (Pydantic)

If your project already uses `pydantic-settings`, you can easily merge the telemetry configuration into your main settings class by inheriting from `WorldlineSettings`. This allows you to validate all environment variables (both app-specific and logging-specific) in one place.

```python
from pydantic_settings import BaseSettings
from worldline import WorldlineSettings

# Inherit from WorldlineSettings to include logging configuration
class Settings(WorldlineSettings, BaseSettings):
    app_name: str = "my-awesome-app"
    database_url: str

# Instantiate your combined settings
settings = Settings()
```
