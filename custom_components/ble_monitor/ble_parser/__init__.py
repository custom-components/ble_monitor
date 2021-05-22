"""Parser for BLE advertisements used by Passive BLE monitor integration."""
import logging
import subprocess

from .atc import ATCParser
from .kegtron import KegtronParser
from .miscale import XiaomiMiScaleParser
from .xiaomi import XiaomiMiBeaconParser
from .qingping import QingpingParser

_LOGGER = logging.getLogger(__name__)


def ble_parser(self, data):
    """Parse the raw data."""

    # check if packet is Extended scan result
    is_ext_packet = True if data[3] == 0x0d else False

    # check for service data of supported manufacturers
    xiaomi_index = data.find(b'\x16\x95\xFE', 15 + 15 if is_ext_packet else 0)
    qingping_index = data.find(b'\x16\xCD\xFD', 15 + 15 if is_ext_packet else 0)
    atc_index = data.find(b'\x16\x1A\x18', 15 + 15 if is_ext_packet else 0)
    miscale_v1_index = data.find(b'\x16\x1D\x18', 15 + 15 if is_ext_packet else 0)
    miscale_v2_index = data.find(b'\x16\x1B\x18', 15 + 15 if is_ext_packet else 0)
    kegtron_index = data.find(b'\x1E\xFF\xFF\xFF', 14 + 15 if is_ext_packet else 0)

    if xiaomi_index != -1:
        return XiaomiMiBeaconParser.decode(self, data, xiaomi_index, is_ext_packet)
    elif qingping_index != -1:
        return QingpingParser.decode(self, data, qingping_index, is_ext_packet)
    elif atc_index != -1:
        return ATCParser.decode(self, data, atc_index, is_ext_packet)
    elif miscale_v1_index != -1:
        return XiaomiMiScaleParser.decode(self, data, miscale_v1_index, is_ext_packet)
    elif miscale_v2_index != -1:
        return XiaomiMiScaleParser.decode(self, data, miscale_v2_index, is_ext_packet)
    elif kegtron_index != -1:
        return KegtronParser.decode(self, data, kegtron_index, is_ext_packet)
    elif self.report_unknown == "Other":
        _LOGGER.info("Unknown advertisement received: %s", data.hex())
        return None, None, None
    else:
        return None, None, None


def hci_get_mac(interface_list=[0]):
    # Get dict of available bluetooth interfaces, returns hci and mac
    btaddress_dict = {}
    output = subprocess.run(["hciconfig"], stdout=subprocess.PIPE).stdout.decode("utf-8")
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
