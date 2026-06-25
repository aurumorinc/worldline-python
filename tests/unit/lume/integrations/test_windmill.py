import os
from unittest import mock

from lume.integrations.windmill import get_windmill_traceparent


@mock.patch.dict(
    os.environ,
    {"WM_TRACEPARENT": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"},
    clear=True,
)
def test_get_windmill_traceparent_valid():
    traceparent = get_windmill_traceparent()
    assert traceparent == "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"


@mock.patch.dict(os.environ, {}, clear=True)
def test_get_windmill_traceparent_missing():
    traceparent = get_windmill_traceparent()
    assert traceparent is None


def test_windmill_facade_re_exported() -> None:
    from lume import get_windmill_traceparent as top_level_fn
    from lume.integrations import get_windmill_traceparent as integrations_fn
    from lume.integrations.windmill import get_windmill_traceparent as real_fn

    assert top_level_fn is real_fn
    assert integrations_fn is real_fn
