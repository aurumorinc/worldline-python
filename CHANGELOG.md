# Changelog v2.0.0

## Breaking Changes

*   **Project Rename from `lume` to `worldline`**
    The project has been renamed. This requires updating all import paths, package references, and repository URLs.
    *   **Migration:** Search and replace all instances of `lume` with `worldline` in your codebase and configuration files.
    *   **Commits:** [31](https://github.com/aurumorinc/worldline-python/commit/31), [32](https://github.com/aurumorinc/worldline-python/commit/32)

*   **Minimum Python Version Upgrade**
    The minimum supported Python version is now 3.11.
    *   **Migration:** Ensure your runtime environment is upgraded to Python 3.11 or higher.
    *   **Commits:** [136](https://github.com/aurumorinc/worldline-python/commit/136), [137](https://github.com/aurumorinc/worldline-python/commit/137), [140](https://github.com/aurumorinc/worldline-python/commit/140)

*   **Removal of `python_logging` Service**
    The `python_logging` service and associated integration modules have been removed.
    *   **Migration:** Remove any dependencies or calls to the `python_logging` module.
    *   **Commits:** [69](https://github.com/aurumorinc/worldline-python/commit/69)

*   **Removal of `langfuse` Integration**
    The `langfuse` integration has been removed from the codebase.
    *   **Migration:** Remove any configuration or code references to `langfuse`.
    *   **Commits:** [17](https://github.com/aurumorinc/worldline-python/commit/17)

*   **Configuration Change: Logging Format**
    Environment-based logging has been replaced by `stdout_format`.
    *   **Migration:** Update your configuration files to remove environment-based logging settings and implement `stdout_format`.
    *   **Commits:** [150](https://github.com/aurumorinc/worldline-python/commit/150)

## Features

*   **Centralized Observability Implementation**
    Implemented centralized observability support for Sentry, PostHog, and Windmill, including a `structlog` proxy.
    *   **Commits:** [70](https://github.com/aurumorinc/worldline-python/commit/70), [41](https://github.com/aurumorinc/worldline-python/commit/41), [40](https://github.com/aurumorinc/worldline-python/commit/40)

*   **New Agent Skills**
    Added specific agent skills to support PostHog, Sentry, Windmill, and `structlog` integrations.
    *   **Commits:** [78](https://github.com/aurumorinc/worldline-python/commit/78), [80](https://github.com/aurumorinc/worldline-python/commit/80), [81](https://github.com/aurumorinc/worldline-python/commit/81)

## Infrastructure

*   **Automated Release Workflow**
    Implemented an automated release workflow to standardize CI processes.
    *   **Commits:** [121](https://github.com/aurumorinc/worldline-python/commit/121), [120](https://github.com/aurumorinc/worldline-python/commit/120), [103](https://github.com/aurumorinc/worldline-python/commit/103)

## Documentation

*   **Architectural and Coding Standards**
    Added comprehensive documentation regarding architectural patterns and coding standards.
    *   **Commits:** [83](https://github.com/aurumorinc/worldline-python/commit/83), [169](https://github.com/aurumorinc/worldline-python/commit/169), [170](https://github.com/aurumorinc/worldline-python/commit/170)
