"""Helpers for ble_monitor."""
import logging
import subprocess

_LOGGER = logging.getLogger(__name__)


# Bluetooth interfaces available on the system
def hci_get_mac(interface_list=[0]):
    """Get dict of available bluetooth interfaces, returns hci and mac."""
    btaddress_dict = {}
    output = subprocess.run(
        ["hciconfig"], stdout=subprocess.PIPE, check=True
    ).stdout.decode("utf-8")

    for interface in interface_list:
        hci_id = "hci{}".format(interface)
        try:
            btaddress_dict[interface] = (
                output.split("{}:".format(hci_id))[1]
                .split("BD Address: ")[1]
                .split(" ")[0]
                .strip()
            )
        except IndexError:
            pass
    return btaddress_dict


try:
    BT_INTERFACES = hci_get_mac([0, 1, 2, 3])
    BT_HCI_INTERFACES = list(BT_INTERFACES.keys())
    BT_MAC_INTERFACES = list(BT_INTERFACES.values())
    DEFAULT_BT_INTERFACE = list(BT_INTERFACES.items())[0][1]
    DEFAULT_HCI_INTERFACE = list(BT_INTERFACES.items())[0][0]
except (IndexError, OSError, subprocess.CalledProcessError):
    BT_INTERFACES = {0: "00:00:00:00:00:00"}
    DEFAULT_BT_INTERFACE = "00:00:00:00:00:00"
    DEFAULT_HCI_INTERFACE = 0
    BT_HCI_INTERFACES = [0]
    BT_MAC_INTERFACES = ["00:00:00:00:00:00"]
    _LOGGER.debug(
        "No Bluetooth interface found. Make sure Bluetooth is installed on your system"
    )
