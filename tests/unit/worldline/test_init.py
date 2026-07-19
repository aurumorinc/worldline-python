import importlib
import os
import sys
from unittest import mock

import pytest

import worldline


@pytest.fixture(autouse=True)
def reset_worldline_init_state():
    """Reset the module-level state before and after each test."""
    if hasattr(sys, "_WORLDLINE_INITIALIZED"):
        delattr(sys, "_WORLDLINE_INITIALIZED")
    yield
    if hasattr(sys, "_WORLDLINE_INITIALIZED"):
        delattr(sys, "_WORLDLINE_INITIALIZED")


@mock.patch.dict(os.environ, {"WORLDLINE_DISABLE_AUTO_INSTRUMENTATION": "true"})
@mock.patch("worldline.service.setup")
def test_init_disabled_via_env(mock_setup):
    """Test that setting WORLDLINE_DISABLE_AUTO_INSTRUMENTATION disables setup."""
    importlib.reload(worldline)
    mock_setup.assert_not_called()
    assert getattr(sys, "_WORLDLINE_INITIALIZED", False) is True


@mock.patch.dict(os.environ, {"WORLDLINE_DISABLE_AUTO_INSTRUMENTATION": "false"})
@mock.patch("worldline.service.setup")
def test_init_executes_setup(mock_setup):
    """Test that setup is called on import."""
    importlib.reload(worldline)
    mock_setup.assert_called_once()
    assert getattr(sys, "_WORLDLINE_INITIALIZED", False) is True


@mock.patch.dict(os.environ, {"WORLDLINE_DISABLE_AUTO_INSTRUMENTATION": "false"})
@mock.patch("worldline.service.setup")
def test_init_catches_setup_exceptions(mock_setup):
    """Test that exceptions during setup are caught and do not crash."""
    mock_setup.side_effect = Exception("Test exception")

    with mock.patch("sys.stderr.write") as mock_stderr:
        importlib.reload(worldline)
        mock_setup.assert_called_once()
        mock_stderr.assert_called_once_with(
            "Worldline auto-instrumentation failed: Test exception\n"
        )
        assert getattr(sys, "_WORLDLINE_INITIALIZED", False) is True


@mock.patch("worldline.service.setup")
def test_init_idempotency(mock_setup):
    """Test that initialization only occurs once."""
    setattr(sys, "_WORLDLINE_INITIALIZED", True)

    importlib.reload(worldline)
    mock_setup.assert_not_called()
