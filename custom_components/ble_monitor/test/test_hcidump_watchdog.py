"""Tests for the raw-HCI inactivity watchdog."""
from unittest.mock import Mock, patch

from ble_monitor.const import (CONF_HCI_INACTIVITY_TIMEOUT,
                               DEFAULT_HCI_INACTIVITY_TIMEOUT, DOMAIN)

from ble_monitor import CONFIG_SCHEMA, HCIdump


def make_hcidump(timeout=60):
    """Create a minimal HCIdump without opening queues or Bluetooth sockets."""
    hcidump = HCIdump.__new__(HCIdump)
    hcidump._inactivity_timeout = timeout
    hcidump._last_hci_activity = {}
    hcidump._joining = False
    hcidump._event_loop = Mock()
    hcidump._watchdog_handle = None
    hcidump.evt_cnt = {}
    return hcidump


def test_watchdog_configuration_defaults_to_sixty_and_accepts_zero():
    """The watchdog is enabled by default and can be explicitly disabled."""
    assert CONFIG_SCHEMA({DOMAIN: {}})[DOMAIN][CONF_HCI_INACTIVITY_TIMEOUT] == (
        DEFAULT_HCI_INACTIVITY_TIMEOUT
    )
    assert CONFIG_SCHEMA(
        {DOMAIN: {CONF_HCI_INACTIVITY_TIMEOUT: 0}}
    )[DOMAIN][CONF_HCI_INACTIVITY_TIMEOUT] == 0


def test_activity_is_tracked_per_adapter_before_packet_validation():
    """Every raw event refreshes only its source adapter, even if malformed."""
    hcidump = make_hcidump()

    with patch("ble_monitor.time.monotonic", return_value=12.5):
        hcidump.process_hci_events(b"short", hci=1)

    assert hcidump._last_hci_activity == {1: 12.5}
    assert hcidump.evt_cnt == {1: 1}


def test_new_activity_extends_timeout_for_one_adapter():
    """Activity on one adapter does not hide another adapter becoming stale."""
    hcidump = make_hcidump(timeout=60)
    hcidump._record_hci_activity(0, now=10)
    hcidump._record_hci_activity(1, now=30)
    hcidump._record_hci_activity(1, now=69)

    assert hcidump._inactive_interfaces(now=70) == [0]


def test_timeout_stops_event_loop_instead_of_rescheduling():
    """An expired watchdog stops the loop so run() reopens the HCI sockets."""
    hcidump = make_hcidump(timeout=60)
    hcidump._record_hci_activity(0, now=1)

    with patch("ble_monitor.time.monotonic", return_value=61):
        hcidump._check_inactivity()

    hcidump._event_loop.stop.assert_called_once_with()
    hcidump._event_loop.call_later.assert_not_called()


def test_zero_timeout_disables_watchdog():
    """A zero timeout neither detects inactivity nor schedules checks."""
    hcidump = make_hcidump(timeout=0)
    hcidump._record_hci_activity(0, now=1)

    assert hcidump._inactive_interfaces(now=1000) == []
    hcidump._schedule_watchdog()
    hcidump._event_loop.call_later.assert_not_called()


def test_shutdown_prevents_watchdog_reschedule():
    """A watchdog callback racing with shutdown does no further work."""
    hcidump = make_hcidump()
    hcidump._joining = True

    hcidump._check_inactivity()

    hcidump._event_loop.stop.assert_not_called()
    hcidump._event_loop.call_later.assert_not_called()


def test_failed_scan_retry_is_rate_limited():
    """Scan setup retries use the fixed delay and stop the current loop."""
    hcidump = make_hcidump()
    handle = Mock()
    hcidump._event_loop.call_later.return_value = handle

    assert hcidump._schedule_scan_retry() is handle
    hcidump._event_loop.call_later.assert_called_once_with(
        hcidump.SCAN_RETRY_INTERVAL, hcidump._event_loop.stop
    )
