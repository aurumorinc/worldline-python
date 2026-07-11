# Changelog v1.0.0

## Breaking Changes

* **Environment Variable Prefix Migration**
  All environment variables previously prefixed with `WM_` have been renamed to `WINDMILL_` to standardize configuration naming conventions.
  * **Migration Path:** Update your deployment configuration files (e.g., Kubernetes manifests, Docker Compose, `.env` files) to reflect the new prefix. For example, `WM_API_KEY` must now be set as `WINDMILL_API_KEY`.
  * **Commits:** [ea61e4a](https://github.com/aurumorinc/worldline-python/commit/ea61e4a1), [e0a3fb0](https://github.com/aurumorinc/worldline-python/commit/e0a3fb02)

## Other

* **Version Bump**
  The package version has been updated to 1.0.0.
  * **Commit:** [bc5d409](https://github.com/aurumorinc/worldline-python/commit/bc5d409a)
