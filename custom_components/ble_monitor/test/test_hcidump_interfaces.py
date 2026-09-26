"""Tests for following Bluetooth adapters that change their hci index."""
from unittest.mock import Mock, patch

from ble_monitor.bt_helpers import hci_get_all_mac, hci_get_mac
from ble_monitor.const import (CONF_ACTIVE_SCAN, CONF_BT_INTERFACE,
                               CONF_HCI_INTERFACE, CONF_REPORT_UNKNOWN)
from btsocket.btmgmt_socket import BluetoothSocketError
from homeassistant.const import CONF_DEVICES, CONF_DISCOVERY

from ble_monitor import HCIdump

DONGLE = "00:E0:43:76:3E:03"
ONBOARD = "E4:5F:01:74:E1:FF"


def make_hcidump(bt_interfaces, hci_interfaces):
    """Create an HCIdump for an adapter configuration without opening sockets."""
    config = {
        CONF_ACTIVE_SCAN: False,
        CONF_BT_INTERFACE: bt_interfaces,
        CONF_DEVICES: [],
        CONF_DISCOVERY: True,
        CONF_HCI_INTERFACE: hci_interfaces,
        CONF_REPORT_UNKNOWN: False,
    }
    dataqueue = {"binary": Mock(), "measuring": Mock(), "tracker": Mock()}
    return HCIdump(config, dataqueue)


def test_adapter_is_followed_to_its_new_hci_index():
    """A re-enumerated adapter is used at its new index, found by its MAC address."""
    hcidump = make_hcidump([DONGLE], [2])

    with patch("ble_monitor.hci_get_all_mac", return_value={0: DONGLE, 1: ONBOARD}):
        hcidump._follow_renumbered_interfaces()

    assert hcidump._interfaces == [0]
    assert hcidump._interface_mac(0) == DONGLE


def test_unchanged_adapter_keeps_its_hci_index():
    """Nothing changes while the adapter is still at its configured index."""
    hcidump = make_hcidump([DONGLE], [2])

    with patch("ble_monitor.hci_get_all_mac", return_value={1: ONBOARD, 2: DONGLE}):
        hcidump._follow_renumbered_interfaces()

    assert hcidump._interfaces == [2]


def test_missing_adapter_keeps_its_hci_index():
    """An adapter that is currently gone keeps its index, so power cycling still applies."""
    hcidump = make_hcidump([DONGLE], [2])

    with patch("ble_monitor.hci_get_all_mac", return_value={1: ONBOARD}):
        hcidump._follow_renumbered_interfaces()

    assert hcidump._interfaces == [2]
    assert hcidump._interface_mac(2) == DONGLE


def test_adapters_swapping_hci_indexes():
    """Two configured adapters that swap their indexes are both followed."""
    hcidump = make_hcidump([DONGLE, ONBOARD], [0, 1])

    with patch("ble_monitor.hci_get_all_mac", return_value={0: ONBOARD, 1: DONGLE}):
        hcidump._follow_renumbered_interfaces()

    assert sorted(hcidump._interfaces) == [0, 1]
    assert hcidump._interface_mac(0) == ONBOARD
    assert hcidump._interface_mac(1) == DONGLE


def test_disabled_bluetooth_does_not_look_up_adapters():
    """Without a Bluetooth adapter, no adapter lookup is done."""
    hcidump = make_hcidump(["disable"], ["disable"])

    with patch("ble_monitor.hci_get_all_mac") as get_all_mac:
        hcidump._follow_renumbered_interfaces()

    get_all_mac.assert_not_called()
    assert hcidump._interfaces == ["disable"]


def test_index_without_known_mac_does_not_raise():
    """An hci index without a known MAC address is logged without a KeyError."""
    hcidump = make_hcidump([], [4])

    with patch("ble_monitor.BT_INTERFACES", {}):
        assert hcidump._interface_mac(4) is None


def test_hci_get_mac_returns_requested_adapters_only():
    """hci_get_mac filters the available adapters, hci_get_all_mac returns all of them."""
    btctl = Mock(presented_list={0: ONBOARD, 4: DONGLE})

    with patch("ble_monitor.bt_helpers.MGMTBluetoothCtl", return_value=btctl):
        assert hci_get_all_mac() == {0: ONBOARD, 4: DONGLE}
        assert hci_get_mac([0, 1, 2, 3]) == {0: ONBOARD}
        assert hci_get_mac() == {0: ONBOARD}


def test_no_adapters_without_management_socket():
    """No adapters are returned when the Bluetooth management socket is unavailable."""
    with patch(
        "ble_monitor.bt_helpers.MGMTBluetoothCtl",
        side_effect=BluetoothSocketError("no socket"),
    ):
        assert hci_get_all_mac() == {}
        assert hci_get_mac([0, 1, 2, 3]) == {}
