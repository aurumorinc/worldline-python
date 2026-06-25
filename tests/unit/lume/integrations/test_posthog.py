def test_posthog_facade_re_exported() -> None:
    from lume import posthog as top_level_posthog
    from lume.integrations import posthog as integrations_posthog

    import posthog as real_posthog

    assert top_level_posthog is real_posthog
    assert integrations_posthog is real_posthog
