"""BT helpers for ble_monitor."""
import logging
import time
from btsocket import btmgmt_sync
from btsocket import btmgmt_protocol
from btsocket.btmgmt_socket import BluetoothSocketError
import pyric.utils.rfkill as rfkill

_LOGGER = logging.getLogger(__name__)


# check rfkill state
def rfkill_list_bluetooth(hci):
    """Execute the rfkill list bluetooth command."""
    hci_idx = f'hci{hci}'
    rfkill_dict = rfkill.rfkill_list()
    try:
        rfkill_hci_state = rfkill_dict[hci_idx]
    except KeyError:
        _LOGGER.error('RF kill switch check failed - no data for %s. Available data: %s', hci_idx, rfkill_dict)
        return None, None
    soft_block = rfkill_hci_state["soft"]
    hard_block = rfkill_hci_state["hard"]
    return soft_block, hard_block


class MGMTBluetoothCtl:
    """Class to control interfaces using the BlueZ management API"""

    def __init__(self, hci):
        self.idx = None
        self.mac = None
        self.presented_list = {}
        idxdata = btmgmt_sync.send('ReadControllerIndexList', None)
        if idxdata.event_frame.status.value != 0x00:  # 0x00 - Success
            _LOGGER.error(
                "Unable to get hci controllers index list! Event frame status: %s",
                idxdata.event_frame.status,
            )
            return
        if idxdata.cmd_response_frame.num_controllers == 0:
            _LOGGER.warning("There are no BT controllers present in the system!")
            return
        hci_idx_list = getattr(idxdata.cmd_response_frame, "controller_index[i]")
        for idx in hci_idx_list:
            hci_info = btmgmt_sync.send('ReadControllerInformation', idx)
            _LOGGER.debug(hci_info)
            bt_le = hci_info.cmd_response_frame.current_settings.get(
                btmgmt_protocol.SupportedSettings.LowEnergy
            )
            if bt_le is not True:
                _LOGGER.warning("hci%i has no (or disabled) BT LE capabilities.")
                continue
            self.presented_list[idx] = hci_info.cmd_response_frame.address
            if hci == idx:
                self.idx = idx
                self.mac = hci_info.cmd_response_frame.address

    @property
    def powered(self):
        """Powered state of the interface"""
        if self.idx is not None:
            response = btmgmt_sync.send('ReadControllerInformation', self.idx)
            return response.cmd_response_frame.current_settings.get(
                btmgmt_protocol.SupportedSettings.Powered
            )
        return None

    @powered.setter
    def powered(self, new_state):
        response = btmgmt_sync.send('SetPowered', self.idx, int(new_state is True))
        if response.event_frame.status.value == 0x00:  # 0x00 - Success
            return True
        return False


# Bluetooth interfaces available on the system
def hci_get_mac(iface_list=None):
    """Get dict of available bluetooth interfaces, returns hci and mac."""
    # Result example: {0: 'F2:67:F3:5B:4D:FC', 1: '00:1A:7D:DA:71:11'}
    try:
        btctl = MGMTBluetoothCtl(0)
    except BluetoothSocketError as error:
        _LOGGER.debug(error)
        return {}
    q_iface_list = iface_list or [0]
    btaddress_dict = {}
    for hci_idx in q_iface_list:
        try:
            btaddress_dict[hci_idx] = btctl.presented_list[hci_idx]
        except KeyError:
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

    adapter = MGMTBluetoothCtl(hci)

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
