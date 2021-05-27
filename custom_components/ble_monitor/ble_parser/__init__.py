"""Parser for BLE advertisements used by Passive BLE monitor integration."""
import logging
import subprocess

from .atc import ATCParser
from .kegtron import parse_kegtron
from .miscale import XiaomiMiScaleParser
from .xiaomi import XiaomiMiBeaconParser
from .qingping import QingpingParser

_LOGGER = logging.getLogger(__name__)


def ble_parser(self, data):
    """Parse the raw data."""
    # check if packet is Extended scan result
    is_ext_packet = True if data[3] == 0x0D else False
    # check for no BR/EDR + LE General discoverable mode flags
    adpayload_start = 29 if is_ext_packet else 14
    # https://www.silabs.com/community/wireless/bluetooth/knowledge-base.entry.html/2017/02/10/bluetooth_advertisin-hGsf
    adpayload_size = data[adpayload_start - 1]
    # check for BTLE msg size
    msg_length = data[2] + 3
    if (
        msg_length <= adpayload_start or msg_length != len(data) or msg_length != (
            adpayload_start + adpayload_size + (0 if is_ext_packet else 1)
        )
    ):
        return None
    # extract RSSI byte
    rssi_index = 18 if is_ext_packet else msg_length - 1
    rssi = data[rssi_index]
    # strange positive RSSI workaround
    if rssi > 127:
        rssi = rssi - 256
    # MAC address
    mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]

    while adpayload_size > 1:
        adstuct_size = data[adpayload_start] + 1
        if adstuct_size > 1 and adstuct_size <= adpayload_size:
            adstruct = data[adpayload_start:adpayload_start + adstuct_size]
            # https://www.bluetooth.com/specifications/assigned-numbers/generic-access-profile/
            adstuct_type = adstruct[1]
            # AD type 'UUI16' https://www.bluetooth.com/specifications/assigned-numbers/
            if adstuct_type == 0x16 and adstuct_size > 4:
                # check for service data of supported manufacturers
                uuid16 = (adstruct[3] << 8) | adstruct[2]
                if uuid16 == 0xFFF9 or uuid16 == 0xFDCD:  # UUID16 = Cleargrass or Qingping
                    qingping_index = data.find(b'\x16\xCD\xFD', 15 + 15 if is_ext_packet else 0)
                    if qingping_index != -1:
                        return QingpingParser.decode(self, data, qingping_index, is_ext_packet)
                    else:
                        return None
                elif uuid16 == 0x181A:  # UUID16 = ATC
                    atc_index = data.find(b'\x16\x1A\x18', 15 + 15 if is_ext_packet else 0)
                    if atc_index != -1:
                        return ATCParser.decode(self, data, atc_index, is_ext_packet)
                    else:
                        return None
                elif uuid16 == 0xFE95:  # UUID16 = Xiaomi
                    xiaomi_index = data.find(b'\x16\x95\xFE', 15 + 15 if is_ext_packet else 0)
                    if xiaomi_index != -1:
                        return XiaomiMiBeaconParser.decode(self, data, xiaomi_index, is_ext_packet)
                    else:
                        return None
                elif uuid16 == 0x181D or uuid16 == 0x181B:  # UUID16 = Miscale
                    miscale_v1_index = data.find(b'\x16\x1D\x18', 15 + 15 if is_ext_packet else 0)
                    miscale_v2_index = data.find(b'\x16\x1B\x18', 15 + 15 if is_ext_packet else 0)
                    if miscale_v1_index != -1:
                        return XiaomiMiScaleParser.decode(self, data, miscale_v1_index, is_ext_packet)
                    elif miscale_v1_index != -1:
                        return XiaomiMiScaleParser.decode(self, data, miscale_v2_index, is_ext_packet)
                    else:
                        return None
            elif adstuct_type == 0xFF:  # AD type 'Manufacturer Specific Data'
                if adstruct[0] == 0x1E and adstruct[2] == 0xFF and adstruct[3] == 0xFF:
                    return parse_kegtron(self, adstruct, mac, rssi)
            elif adstuct_type > 0x3D:
                # AD type not standard
                if self.report_unknown == "Other":
                    _LOGGER.info("Unknown advertisement received: %s", data.hex())
                return None
        adpayload_size -= adstuct_size
        adpayload_start += adstuct_size
    return None


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
