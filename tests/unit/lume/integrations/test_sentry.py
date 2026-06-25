def test_sentry_facade_re_exported() -> None:
    from lume import sentry_sdk as top_level_sentry_sdk
    from lume.integrations import sentry_sdk as integrations_sentry_sdk

    import sentry_sdk as real_sentry_sdk

    assert top_level_sentry_sdk is real_sentry_sdk
    assert integrations_sentry_sdk is real_sentry_sdk
