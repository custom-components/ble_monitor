"""Parser for passive BLE advertisements."""
import logging

from .atc import parse_atc
from .bluemaestro import parse_bluemaestro
from .brifit import parse_brifit
from .govee import parse_govee
from .inkbird import parse_inkbird
from .inode import parse_inode
from .jinou import parse_jinou
from .kegtron import parse_kegtron
from .miscale import parse_miscale
from .moat import parse_moat
from .oral_b import parse_oral_b
from .qingping import parse_qingping
from .ruuvitag import parse_ruuvitag
from .sensorpush import parse_sensorpush
from .teltonika import parse_teltonika
from .thermoplus import parse_thermoplus
from .xiaomi import parse_xiaomi
from .xiaogui import parse_xiaogui
from .bparasite import parse_bparasite
from .ibeacon import parse_ibeacon
from .altbeacon import parse_altbeacon

_LOGGER = logging.getLogger(__name__)


class BleParser:
    """Parser for BLE advertisements"""
    def __init__(
        self,
        report_unknown=False,
        discovery=True,
        filter_duplicates=False,
        sensor_whitelist=[],
        tracker_whitelist=[],
        aeskeys={}
    ):
        self.report_unknown = report_unknown
        self.discovery = discovery
        self.filter_duplicates = filter_duplicates
        self.sensor_whitelist = sensor_whitelist
        self.tracker_whitelist = tracker_whitelist
        self.aeskeys = aeskeys

        self.lpacket_ids = {}
        self.movements_list = {}
        self.adv_priority = {}

    def parse_data(self, data):
        """Parse the raw data."""
        # check if packet is Extended scan result
        is_ext_packet = True if data[3] == 0x0D else False
        # check for no BR/EDR + LE General discoverable mode flags
        adpayload_start = 29 if is_ext_packet else 14
        # https://www.silabs.com/community/wireless/bluetooth/knowledge-base.entry.html/2017/02/10/bluetooth_advertisin-hGsf
        try:
            adpayload_size = data[adpayload_start - 1]
        except IndexError:
            return None, None
        # check for BTLE msg size
        msg_length = data[2] + 3
        if (
            msg_length <= adpayload_start or msg_length != len(data) or msg_length != (
                adpayload_start + adpayload_size + (0 if is_ext_packet else 1)
            )
        ):
            return None, None
        # extract RSSI byte
        rssi_index = 18 if is_ext_packet else msg_length - 1
        rssi = data[rssi_index]
        # strange positive RSSI workaround
        if rssi > 127:
            rssi = rssi - 256
        # MAC address
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        sensor_data = None
        tracker_data = None
        complete_local_name = ""
        service_class_uuid16 = None
        service_class_uuid128 = None
        service_data = b''
        man_spec_data_list = []
        unknown_sensor = False

        while adpayload_size > 1:
            adstuct_size = data[adpayload_start] + 1
            if adstuct_size > 1 and adstuct_size <= adpayload_size:
                adstruct = data[adpayload_start:adpayload_start + adstuct_size]
                # https://www.bluetooth.com/specifications/assigned-numbers/generic-access-profile/
                adstuct_type = adstruct[1]
                if adstuct_type == 0x02:
                    # AD type 'Incomplete List of 16-bit Service Class UUIDs'
                    service_class_uuid16 = (adstruct[2] << 8) | adstruct[3]
                elif adstuct_type == 0x03:
                    # AD type 'Complete List of 16-bit Service Class UUIDs'
                    service_class_uuid16 = (adstruct[2] << 8) | adstruct[3]
                elif adstuct_type == 0x06:
                    # AD type '128-bit Service Class UUIDs'
                    service_class_uuid128 = adstruct[2:]
                elif adstuct_type == 0x09:
                    # AD type 'complete local name'
                    complete_local_name = adstruct[2:].decode("utf-8")
                elif adstuct_type == 0x16 and adstuct_size > 4:
                    # AD type 'Service Data - 16-bit UUID'
                    uuid16 = (adstruct[3] << 8) | adstruct[2]
                    service_data += adstruct
                elif adstuct_type == 0xFF:
                    # AD type 'Manufacturer Specific Data'
                    man_spec_data_list.append(adstruct)
                    # https://www.bluetooth.com/specifications/assigned-numbers/company-identifiers/
            adpayload_size -= adstuct_size
            adpayload_start += adstuct_size

        while not sensor_data:
            if service_data:
                # parse data for sensors with service data
                if uuid16 == 0xFFF9 or uuid16 == 0xFDCD:  # UUID16 = Cleargrass or Qingping
                    sensor_data = parse_qingping(self, service_data, mac, rssi)
                    break
                elif uuid16 == 0x181A:  # UUID16 = ATC or b-parasite
                    if len(service_data) == 22 or len(service_data) == 20:
                        sensor_data = parse_bparasite(self, service_data, mac, rssi)
                    else:
                        sensor_data = parse_atc(self, service_data, mac, rssi)
                    break
                elif uuid16 == 0xFE95:  # UUID16 = Xiaomi
                    sensor_data = parse_xiaomi(self, service_data, mac, rssi)
                    break
                elif uuid16 == 0x181D or uuid16 == 0x181B:  # UUID16 = Mi Scale
                    sensor_data = parse_miscale(self, service_data, mac, rssi)
                    break
                elif uuid16 == 0xFEAA:  # UUID16 = Ruuvitag V2/V4
                    sensor_data = parse_ruuvitag(self, service_data, mac, rssi)
                    break
                elif uuid16 == 0x2A6E or uuid16 == 0x2A6F:  # UUID16 = Teltonika
                    # Teltonika can contain multiple sevice data payloads in one advertisement
                    sensor_data = parse_teltonika(self, service_data, complete_local_name, mac, rssi)
                    break
                else:
                    unknown_sensor = True
            elif man_spec_data_list:
                for man_spec_data in man_spec_data_list:
                    # parse data for sensors with manufacturer specific data
                    comp_id = (man_spec_data[3] << 8) | man_spec_data[2]
                    if comp_id == 0x4C and man_spec_data[4] == 0x02:  # iBeacon
                        sensor_data, tracker_data = parse_ibeacon(self, man_spec_data, mac, rssi)
                        break
                    elif man_spec_data[0] == 0x1B and ((man_spec_data[4] << 8) | man_spec_data[5]) == 0xBEAC:  # AltBeacon
                        sensor_data, tracker_data = parse_altbeacon(self, man_spec_data, comp_id, mac, rssi)
                        break
                    elif man_spec_data[0] == 0x1E and comp_id == 0xFFFF:  # Kegtron
                        sensor_data = parse_kegtron(self, man_spec_data, mac, rssi)
                        break
                    elif service_class_uuid16 == 0xF0FF:
                        if man_spec_data[0] in [0x15, 0x17] and comp_id in [0x0010, 0x0011, 0x0015]:  # Thermoplus
                            sensor_data = parse_thermoplus(self, man_spec_data, mac, rssi)
                            break
                        elif man_spec_data[0] in [0x0D, 0x0F, 0x13, 0x17] and (
                            comp_id in [0x0000, 0x0001] or complete_local_name == "iBBQ"
                        ):  # Inkbird iBBQ
                            sensor_data = parse_inkbird(self, man_spec_data, mac, rssi)
                            break
                        else:
                            unknown_sensor = True
                    elif man_spec_data[0] == 0x0A and complete_local_name == "sps":  # Inkbird IBS-TH
                        sensor_data = parse_inkbird(self, man_spec_data, mac, rssi)
                        break
                    elif man_spec_data[0] == 0x0C and comp_id == 0xEC88:  # Govee H5051
                        sensor_data = parse_govee(self, man_spec_data, mac, rssi)
                        break
                    elif man_spec_data[0] == 0x0A and comp_id == 0xEC88:  # Govee H5051/H5074
                        sensor_data = parse_govee(self, man_spec_data, mac, rssi)
                        break
                    elif man_spec_data[0] == 0x09 and comp_id == 0xEC88:  # Govee H5072/H5075
                        sensor_data = parse_govee(self, man_spec_data, mac, rssi)
                        break
                    elif man_spec_data[0] == 0x09 and comp_id == 0x0001:  # Govee H5101/H5102/H5177
                        sensor_data = parse_govee(self, man_spec_data, mac, rssi)
                        break
                    elif man_spec_data[0] == 0x0C and comp_id == 0x0001:  # Govee H5178
                        sensor_data = parse_govee(self, man_spec_data, mac, rssi)
                        break
                    elif man_spec_data[0] == 0x0C and comp_id == 0x8801:  # Govee H5179
                        sensor_data = parse_govee(self, man_spec_data, mac, rssi)
                        break
                    elif man_spec_data[0] == 0x11 and service_class_uuid16 == 0x5183:  # Govee H5183
                        sensor_data = parse_govee(self, man_spec_data, mac, rssi)
                        break
                    elif comp_id == 0x0499:  # Ruuvitag V3/V5
                        sensor_data = parse_ruuvitag(self, man_spec_data, mac, rssi)
                        break
                    elif man_spec_data[0] == 0x14 and (comp_id == 0xaa55):  # Brifit
                        sensor_data = parse_brifit(self, man_spec_data, mac, rssi)
                        break
                    elif man_spec_data[0] == 0x0E and man_spec_data[3] == 0x82:  # iNode
                        sensor_data = parse_inode(self, man_spec_data, mac, rssi)
                        break
                    elif man_spec_data[0] == 0x19 and man_spec_data[3] in [
                        0x91, 0x92, 0x93, 0x94, 0x95, 0x96, 0x9A, 0x9B, 0x9C, 0x9D
                    ]:  # iNode Care Sensors
                        sensor_data = parse_inode(self, man_spec_data, mac, rssi)
                        break
                    elif man_spec_data[0] == 0x0E and service_class_uuid16 == 0x20AA:  # Jinou BEC07-5
                        sensor_data = parse_jinou(self, man_spec_data, mac, rssi)
                        break
                    elif man_spec_data[0] == 0x15 and comp_id == 0x1000:  # Moat S2
                        sensor_data = parse_moat(self, man_spec_data, mac, rssi)
                        break
                    elif man_spec_data[0] == 0x11 and comp_id == 0x0133:  # BlueMaestro
                        sensor_data = parse_bluemaestro(self, man_spec_data, mac, rssi)
                        break
                    elif man_spec_data[0] == 0x10 and adstruct[2] == 0xC0:  # Xiaogui Scale
                        sensor_data = parse_xiaogui(self, man_spec_data, mac, rssi)
                        break
                    elif man_spec_data[0] == 0x0E and comp_id == 0x00DC:  # Oral-b
                        sensor_data = parse_oral_b(self, man_spec_data, mac, rssi)
                        break
                    elif man_spec_data[0] in [0x06, 0x08] and service_class_uuid128 == b'\xb0\x0a\x09\xec\xd7\x9d\xb8\x93\xba\x42\xd6\x11\x00\x00\x09\xef':  # Sensorpush
                        sensor_data = parse_sensorpush(self, man_spec_data, mac, rssi)
                        break
                    else:
                        unknown_sensor = True
            else:
                unknown_sensor = True
            if unknown_sensor and self.report_unknown == "Other":
                _LOGGER.info("Unknown advertisement received: %s", data.hex())
            break

        # check for monitored device trackers
        tracker_id = tracker_data['tracker_id'] if tracker_data and 'tracker_id' in tracker_data else mac
        if tracker_id in self.tracker_whitelist:
            if tracker_data is not None:
                tracker_data.update({"is connected": True})
            else:
                tracker_data = {
                    "is connected": True,
                    "mac": ''.join('{:02X}'.format(x) for x in mac),
                    "rssi": rssi,
                }
        else:
            tracker_data = None

        return sensor_data, tracker_data
