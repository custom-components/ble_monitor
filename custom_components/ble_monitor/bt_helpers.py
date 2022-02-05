"""BT helpers for ble_monitor."""
import logging
import time
from pydbus import SystemBus
from pyric.utils import rfkill

_LOGGER = logging.getLogger(__name__)
BUS_NAME = 'org.bluez'
OBJ_MANAGER = 'org.freedesktop.DBus.ObjectManager'


# check rfkill state
def rfkill_list_bluetooth(hci):
    """Execute the rfkill list bluetooth command."""
    hci_idx = f'hci{hci}'
    rfkill_dict = rfkill.rfkill_list()
    try:
        rfkill_hci_state = rfkill_dict[hci_idx]
    except IndexError:
        _LOGGER.error('RF kill switch check failed - no data for %s. Available data: %s', hci_idx, rfkill_dict)
    soft_block = rfkill_hci_state["soft"]
    hard_block = rfkill_hci_state["hard"]
    return soft_block, hard_block


class DBusBluetoothCtl:
    """Class to control interfaces using the BlueZ DBus API"""

    def __init__(self, hci):
        bus = SystemBus()
        bluez = bus.get(BUS_NAME, '/')
        manager = bluez[OBJ_MANAGER]
        managed_objects = manager.GetManagedObjects()
        self._adapter = None
        self.mac = None
        self.presented_list = {}
        for path, _ in managed_objects.items():
            if "hci" in path:
                hci_idx = int(path.split("hci")[1])  # int(path[-1]) works only for 0..9
                self._adapter = bus.get(BUS_NAME, path)
                self.presented_list[hci_idx] = self._adapter.Address
                if hci == hci_idx:
                    self.mac = self._adapter.Address
                    return

    @property
    def powered(self):
        """Powered state of the interface"""
        if self.mac is not None:
            return self._adapter.Powered
        return None

    @powered.setter
    def powered(self, new_state):
        self._adapter.Powered = new_state


# Bluetooth interfaces available on the system
def hci_get_mac(iface_list=None):
    """Get dict of available bluetooth interfaces, returns hci and mac."""
    # Result example: {0: 'F2:67:F3:5B:4D:FC', 1: '00:1A:7D:DA:71:11'}
    btctl = DBusBluetoothCtl(0)
    q_iface_list = iface_list or [0]
    btaddress_dict = {}
    for hci_idx in q_iface_list:
        try:
            btaddress_dict[hci_idx] = btctl.presented_list[hci_idx]
        except IndexError:
            pass
    return btaddress_dict


def reset_bluetooth(hci):
    """Resetting the Bluetooth adapter."""
    _LOGGER.debug("resetting Bluetooth")

    soft_block, hard_block = rfkill_list_bluetooth(hci)
    if soft_block is True:
        _LOGGER.warning("bluetooth adapter is soft blocked!")
        return
    if hard_block is True:
        _LOGGER.warning("bluetooth adapter is hard blocked!")
        return

    adapter = DBusBluetoothCtl(hci)

    if adapter.mac is None:
        _LOGGER.error(
            "hci%i seems not to exist (anymore), check BT interface mac address in your settings. "
            "Available adapters: %s ",
            hci,
            adapter.presented_list,
        )
        return

    pstate_before = adapter.powered
    if pstate_before is True:
        _LOGGER.debug("Power state of bluetooth adapter is ON.")
        adapter.powered = False
        time.sleep(2)
    elif pstate_before is False:
        _LOGGER.debug(
            "Power state of bluetooth adapter is OFF, trying to turn it back ON."
        )
    else:
        _LOGGER.debug(
            "Power state of bluetooth adapter could not be determined."
        )
        return

    adapter.powered = True
    time.sleep(3)

    # Check the state after the reset
    pstate_after = adapter.powered
    if pstate_after is True:
        _LOGGER.debug("Power state of bluetooth adapter is ON after resetting.")
    elif pstate_after is False:
        _LOGGER.debug("Power state of bluetooth adapter is OFF after resetting.")
    else:
        _LOGGER.debug(
            "Power state of bluetooth adapter could not be determined after resetting."
        )


BT_INTERFACES = hci_get_mac([0, 1, 2, 3])
if BT_INTERFACES:
    DEFAULT_BT_INTERFACE = list(BT_INTERFACES.items())[0][1]
    DEFAULT_HCI_INTERFACE = list(BT_INTERFACES.items())[0][0]
    BT_MULTI_SELECT = {value: f'{value} (hci{key})' for (key, value) in BT_INTERFACES.items()}
else:
    DEFAULT_BT_INTERFACE = "disable"
    DEFAULT_HCI_INTERFACE = "disable"
    BT_MULTI_SELECT = {}
    _LOGGER.debug(
        "No Bluetooth interface found. Make sure Bluetooth is installed on your system"
    )
BT_MULTI_SELECT["disable"] = "Don't use Bluetooth adapter"
