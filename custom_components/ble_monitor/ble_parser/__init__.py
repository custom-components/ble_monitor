"""Parser for BLE advertisements used by Passive BLE monitor integration."""
import logging
import subprocess

from .atc import parse_atc
from .kegtron import parse_kegtron
from .miscale import parse_miscale
from .xiaomi import parse_xiaomi
from .qingping import parse_qingping
from .thermoplus import parse_thermoplus

_LOGGER = logging.getLogger(__name__)


def ble_parser(self, data):
    """Parse the raw data."""
    # check if packet is Extended scan result
    is_ext_packet = True if data[3] == 0x0D else False
    # check for no BR/EDR + LE General discoverable mode flags
    adpayload_start = 29 if is_ext_packet else 14
    # https://www.silabs.com/community/wireless/bluetooth/knowledge-base.entry.html/2017/02/10/bluetooth_advertisin-hGsf
    try:
        adpayload_size = data[adpayload_start - 1]
    except IndexError:
        return None
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
            if adstuct_type == 0x16 and adstuct_size > 4:
                # AD type 'UUI16' https://www.bluetooth.com/specifications/assigned-numbers/
                uuid16 = (adstruct[3] << 8) | adstruct[2]
                # check for service data of supported manufacturers
                if uuid16 == 0xFFF9 or uuid16 == 0xFDCD:  # UUID16 = Cleargrass or Qingping
                    return parse_qingping(self, adstruct, mac, rssi)
                elif uuid16 == 0x181A:  # UUID16 = ATC
                    return parse_atc(self, adstruct, mac, rssi)
                elif uuid16 == 0xFE95:  # UUID16 = Xiaomi
                    return parse_xiaomi(self, adstruct, mac, rssi)
                elif uuid16 == 0x181D or uuid16 == 0x181B:  # UUID16 = Mi Scale
                    return parse_miscale(self, adstruct, mac, rssi)
            elif adstuct_type == 0xFF:
                # AD type 'Manufacturer Specific Data' with company identifier 
                # https://www.bluetooth.com/specifications/assigned-numbers/company-identifiers/
                comp_id = (adstruct[3] << 8) | adstruct[2]
                # check for service data of supported companies
                if adstruct[0] == 0x1E and comp_id == 0xFFFF:  # Kegtron
                    return parse_kegtron(self, adstruct, mac, rssi)
                if adstruct[0] == 0x15 and (comp_id == 0x0010 or comp_id == 0x0011):  # Thermoplus
                    return parse_thermoplus(self, adstruct, mac, rssi)
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
