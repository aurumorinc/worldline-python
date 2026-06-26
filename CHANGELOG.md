# Changelog v3.0.1

## Breaking Changes

* **Renaming of Windmill Environment Variables**
  All environment variables prefixed with `WM_` have been renamed to use the `WINDMILL_` prefix to align with updated naming conventions.
  * **Migration Guide:** Update your deployment configurations (e.g., Docker Compose, Kubernetes ConfigMaps, or `.env` files) by replacing the `WM_` prefix with `WINDMILL_` for all Windmill-related settings.
  * **Commits:** [ea61e4a](https://github.com/aurumorinc/worldline-python/commit/ea61e4a1), [e0a3fb0](https://github.com/aurumorinc/worldline-python/commit/e0a3fb02)
