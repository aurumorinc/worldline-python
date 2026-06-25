def test_langfuse_facade_re_exported() -> None:
    from lume import langfuse as top_level_langfuse
    from lume import observe as top_level_observe
    from lume.integrations import langfuse as integrations_langfuse
    from lume.integrations import observe as integrations_observe

    import langfuse as real_langfuse
    from langfuse import observe as real_observe

    assert top_level_langfuse is real_langfuse
    assert integrations_langfuse is real_langfuse

    assert top_level_observe is real_observe
    assert integrations_observe is real_observe
