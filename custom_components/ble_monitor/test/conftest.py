"""Pytest configuration for BLE monitor tests."""
import pytest


@pytest.fixture(autouse=True)
def enable_event_loop_debug():
    """Override the async autouse fixture from pytest-homeassistant-custom-component.

    All BLE monitor tests are synchronous and do not need an event loop.
    This sync override prevents pytest 9 from raising an error when async
    fixtures are requested by sync tests.
    """
