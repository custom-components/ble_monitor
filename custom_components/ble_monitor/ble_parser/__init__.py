"""Parser for passive BLE advertisements."""
import logging
from typing import Optional

from .acconeer import parse_acconeer
from .airmentor import parse_airmentor
from .almendo import parse_almendo
from .altbeacon import parse_altbeacon
from .amazfit import parse_amazfit
from .atc import parse_atc
from .beckett import parse_beckett
from .bluemaestro import parse_bluemaestro
from .blustream import parse_blustream
from .bparasite import parse_bparasite
from .bthome import parse_bthome
from .chefiq import parse_chefiq
from .const import JAALEE_TYPES, TILT_TYPES
from .govee import parse_govee
from .grundfos import parse_grundfos
from .helpers import to_mac, to_unformatted_mac, to_uuid
from .hhcc import parse_hhcc
from .holyiot import parse_holyiot
from .hormann import parse_hormann
from .ibeacon import parse_ibeacon
from .inkbird import parse_inkbird
from .inode import parse_inode
from .jaalee import parse_jaalee
from .jinou import parse_jinou
from .kegtron import parse_kegtron
from .kkm import parse_kkm
from .laica import parse_laica
from .mikrotik import parse_mikrotik
from .miscale import parse_miscale
from .moat import parse_moat
from .oral_b import parse_oral_b
from .oras import parse_oras
from .qingping import parse_qingping
from .relsib import parse_relsib
from .ruuvitag import parse_ruuvitag
from .sensirion import parse_sensirion
from .sensorpush import parse_sensorpush
from .senssun import parse_senssun
from .smartdry import parse_smartdry
from .switchbot import parse_switchbot
from .teltonika import parse_teltonika
from .thermobeacon import parse_thermobeacon
from .thermopro import parse_thermopro
from .tilt import parse_tilt
from .xiaogui import parse_xiaogui
from .xiaomi import parse_xiaomi

_LOGGER = logging.getLogger(__name__)


class BleParser:
    """Parser for BLE advertisements"""
    def __init__(
        self,
        report_unknown=False,
        discovery=True,
        filter_duplicates=False,
        sensor_whitelist=None,
        tracker_whitelist=None,
        report_unknown_whitelist=None,
        aeskeys=None
    ):
        self.report_unknown = report_unknown
        self.discovery = discovery
        self.filter_duplicates = filter_duplicates
        if sensor_whitelist is None:
            self.sensor_whitelist = []
        else:
            self.sensor_whitelist = sensor_whitelist
        if tracker_whitelist is None:
            self.tracker_whitelist = []
        else:
            self.tracker_whitelist = tracker_whitelist
        if report_unknown_whitelist is None:
            self.report_unknown_whitelist = []
        else:
            self.report_unknown_whitelist = report_unknown_whitelist
        if aeskeys is None:
            self.aeskeys = {}
        else:
            self.aeskeys = aeskeys

        self.lpacket_ids = {}
        self.movements_list = {}
        self.adv_priority = {}
        self.no_key_message = []

    def parse_raw_data(self, data):
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
        complete_local_name = ""
        shortened_local_name = ""
        service_class_uuid16 = None
        service_class_uuid128 = None
        service_data_list = []
        man_spec_data_list = []

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
                elif adstuct_type == 0x08:
                    # AD type 'shortened local name'
                    try:
                        shortened_local_name = adstruct[2:].decode("utf-8")
                    except UnicodeDecodeError:
                        shortened_local_name = ""
                elif adstuct_type == 0x09:
                    # AD type 'complete local name'
                    try:
                        complete_local_name = adstruct[2:].decode("utf-8")
                    except UnicodeDecodeError:
                        complete_local_name = ""
                elif adstuct_type == 0x16 and adstuct_size > 4:
                    # AD type 'Service Data - 16-bit UUID'
                    service_data_list.append(adstruct)
                elif adstuct_type == 0xFF:
                    # AD type 'Manufacturer Specific Data'
                    man_spec_data_list.append(adstruct)
                    # https://www.bluetooth.com/specifications/assigned-numbers/company-identifiers/
            adpayload_size -= adstuct_size
            adpayload_start += adstuct_size

        if complete_local_name:
            local_name = complete_local_name
        else:
            local_name = shortened_local_name

        sensor_data, tracker_data = self.parse_advertisement(
            mac,
            rssi,
            service_class_uuid16,
            service_class_uuid128,
            local_name,
            service_data_list,
            man_spec_data_list
        )
        return sensor_data, tracker_data

    def parse_advertisement(
            self,
            mac: bytes,
            rssi: int,
            service_class_uuid16: Optional[int] = None,
            service_class_uuid128: Optional[bytes] = None,
            local_name: Optional[str] = "",
            service_data_list: Optional[list] = None,
            man_spec_data_list: Optional[list] = None
    ):
        """parse BLE advertisement"""
        sensor_data = {}
        tracker_data = {}
        uuid = None
        unknown_sensor = False
        if service_data_list is None:
            service_data_list = []
        if man_spec_data_list is None:
            man_spec_data_list = []

        while not sensor_data:
            if service_data_list:
                for service_data in service_data_list:
                    # parse data for sensors with service data
                    uuid16 = (service_data[3] << 8) | service_data[2]
                    if uuid16 == 0x1809:
                        # UUID16 = Health Thermometer service (used by Relsib)
                        if len(service_data_list) == 3:
                            uuid16_2 = (service_data_list[1][3] << 8) | service_data_list[1][2]
                            if uuid16_2 == 0x181A:
                                service_data = b"".join(service_data_list)
                        sensor_data = parse_relsib(self, service_data, mac)
                        break
                    if uuid16 == 0x181A:
                        # UUID16 = Environmental Sensing (used by ATC or b-parasite)
                        if len(service_data) == 22 or len(service_data) == 20:
                            sensor_data = parse_bparasite(self, service_data, mac)
                        else:
                            sensor_data = parse_atc(self, service_data, mac)
                        break
                    elif uuid16 in [0x181B, 0x181D]:
                        # UUID16 = Body Composition and Weight Scale (used by Mi Scale)
                        sensor_data = parse_miscale(self, service_data, mac)
                        break
                    elif uuid16 in [0x181C, 0x181E]:
                        # UUID16 = User Data and Bond Management (used by BTHome)
                        sensor_data = parse_bthome(self, service_data, uuid16, mac)
                        break
                    elif uuid16 == 0x5242:
                        # UUID16 = HolyIOT
                        sensor_data = parse_holyiot(self, service_data, mac)
                        break
                    elif uuid16 in [0xAA20, 0xAA21, 0xAA22] and local_name == "ECo":
                        # UUID16 = Relsib
                        sensor_data = parse_relsib(self, service_data, mac)
                        break
                    elif uuid16 in [0xF51C, 0xF525]:
                        # UUID16 = Jaalee
                        sensor_data = parse_jaalee(self, service_data, mac)
                        break
                    elif uuid16 == 0xFCD2:
                        # UUID16 = Allterco Robotics ltd (BTHome V2)
                        sensor_data = parse_bthome(self, service_data, uuid16, mac)
                        break
                    elif uuid16 in [0xFD3D, 0x0D00]:
                        # UUID16 = unknown (used by Switchbot)
                        sensor_data = parse_switchbot(self, service_data, mac)
                        break
                    elif uuid16 == 0xFD50:
                        # UUID16 = Hangzhou Tuya Information Technology Co., Ltd (HHCC)
                        sensor_data = parse_hhcc(self, service_data, mac)
                        break
                    elif uuid16 == 0xFDCD:
                        # UUID16 = Qingping
                        sensor_data = parse_qingping(self, service_data, mac)
                        break
                    elif uuid16 == 0xFE95:
                        # UUID16 = Xiaomi
                        sensor_data = parse_xiaomi(self, service_data, mac)
                        break
                    elif uuid16 == 0xFEAA:
                        if len(service_data) == 19:
                            # UUID16 = Google (used by KKM)
                            sensor_data = parse_kkm(self, service_data, mac)
                            break
                        elif len(service_data) >= 23:
                            # UUID16 = Google (used by Ruuvitag V2/V4)
                            sensor_data = parse_ruuvitag(self, service_data, mac)
                            break
                    elif uuid16 == 0xFEE0:
                        # UUID16 = Anhui Huami Information Technology Co., Ltd. (Amazfit)
                        if man_spec_data_list:
                            man_spec_data = man_spec_data_list[0]
                        else:
                            man_spec_data = None
                        sensor_data = parse_amazfit(self, service_data, man_spec_data, mac)
                    elif uuid16 == 0xFFF9:
                        # UUID16 = FIDO (used by Cleargrass)
                        sensor_data = parse_qingping(self, service_data, mac)
                        break
                    elif uuid16 == 0x2A6E or uuid16 == 0x2A6F:
                        # UUID16 = Temperature and Humidity (used by Teltonika)
                        if len(service_data_list) == 2:
                            service_data = b"".join(service_data_list)
                        sensor_data = parse_teltonika(self, service_data, local_name, mac)
                        break
                    else:
                        unknown_sensor = True
            elif man_spec_data_list:
                for man_spec_data in man_spec_data_list:
                    # parse data for sensors with manufacturer specific data
                    comp_id = (man_spec_data[3] << 8) | man_spec_data[2]
                    data_len = man_spec_data[0]
                    # Filter on Company Identifier
                    if comp_id == 0x0001 and data_len in [0x09, 0x0C, 0x22, 0x25]:
                        # Govee H5101/H5102/H5106/H5177
                        sensor_data = parse_govee(self, man_spec_data, service_class_uuid16, local_name, mac)
                        break
                    elif comp_id == 0x004C and man_spec_data[4] == 0x02:
                        # iBeacon
                        if int.from_bytes(man_spec_data[6:22], byteorder='big') in TILT_TYPES:
                            # Tilt
                            sensor_data, tracker_data = parse_tilt(self, man_spec_data, mac)
                            uuid = man_spec_data[6:22]
                            break
                        elif int.from_bytes(man_spec_data[6:22], byteorder='big') in JAALEE_TYPES:
                            # Jaalee
                            sensor_data = parse_jaalee(self, man_spec_data, mac)
                            break
                        elif len(man_spec_data_list) == 2:
                            # Teltonika Eye (can send both iBeacon and Teltonika data in one message)
                            second_man_spec_data = man_spec_data_list[1]
                            second_comp_id = (second_man_spec_data[3] << 8) | second_man_spec_data[2]
                            if second_comp_id == 0x089A:
                                sensor_data = parse_teltonika(self, second_man_spec_data, local_name, mac)
                                break
                        else:
                            # iBeacon
                            sensor_data, tracker_data = parse_ibeacon(self, man_spec_data, mac)
                            uuid = man_spec_data[6:22]
                            break
                    elif comp_id == 0x00DC and data_len == 0x0E:
                        # Oral-b
                        sensor_data = parse_oral_b(self, man_spec_data, mac)
                        break
                    elif comp_id == 0x05CD and data_len == 0x15:
                        # Chef iQ
                        sensor_data = parse_chefiq(self, man_spec_data, mac)
                        break
                    elif comp_id == 0x0131:
                        # Oras
                        sensor_data = parse_oras(self, man_spec_data, mac)
                        break
                    elif comp_id == 0x0157 and data_len == 0x1B:
                        # Miband
                        sensor_data = parse_amazfit(self, None, man_spec_data, mac)
                        break
                    elif comp_id == 0x0194 and data_len == 0x0C:
                        # Blustream
                        sensor_data = parse_blustream(self, man_spec_data, mac)
                        break
                    elif comp_id == 0x0499:
                        # Ruuvitag V3/V5
                        sensor_data = parse_ruuvitag(self, man_spec_data, mac)
                        break
                    elif comp_id == 0x0757:
                        # Teltonika (Ela rebrand)
                        if len(man_spec_data_list) == 2:
                            man_spec_data = b"".join(man_spec_data_list)
                        sensor_data = parse_teltonika(self, man_spec_data, local_name, mac)
                        break
                    elif comp_id == 0x07B4:
                        # Hörmann
                        if len(man_spec_data_list) == 2:
                            man_spec_data = b"".join(man_spec_data_list)
                        sensor_data = parse_hormann(self, man_spec_data, mac)
                        break
                    elif comp_id == 0x089A:
                        # Teltonika
                        sensor_data = parse_teltonika(self, man_spec_data, local_name, mac)
                        break
                    elif comp_id == 0x094F and data_len == 0x15:
                        # Mikrotik
                        sensor_data = parse_mikrotik(self, man_spec_data, mac)
                        break
                    elif comp_id == 0x06E8:
                        # Almendo (Blusensor)
                        sensor_data = parse_almendo(self, man_spec_data, mac)
                        break
                    elif comp_id == 0x1000 and data_len == 0x15:
                        # Moat S2
                        sensor_data = parse_moat(self, man_spec_data, mac)
                        break
                    elif comp_id == 0x0133 and data_len in [0x11, 0x15]:
                        # BlueMaestro
                        sensor_data = parse_bluemaestro(self, man_spec_data, mac)
                        break
                    elif comp_id == 0x01AE and data_len == 0x0F:
                        # SmartDry
                        sensor_data = parse_smartdry(self, man_spec_data, mac)
                        break
                    elif comp_id == 0x06D5:
                        # Sensirion
                        sensor_data = parse_sensirion(self, man_spec_data, local_name, mac)
                        break
                    elif comp_id in [0x2111, 0x2112, 0x2121, 0x2122] and data_len == 0x0B:
                        # Air Mentor
                        sensor_data = parse_airmentor(self, man_spec_data, mac)
                        break
                    elif comp_id == 0x2730 and data_len in [0x14, 0x2D]:
                        # Govee H5182
                        sensor_data = parse_govee(self, man_spec_data, service_class_uuid16, local_name, mac)
                        break
                    elif comp_id == 0x1B36 and data_len in [0x14, 0x2D]:
                        # Govee H5184
                        sensor_data = parse_govee(self, man_spec_data, service_class_uuid16, local_name, mac)
                        break
                    elif comp_id in [0x4A32, 0x332, 0x4C32] and data_len in [0x17, 0x2D]:
                        # Govee H5185
                        sensor_data = parse_govee(self, man_spec_data, service_class_uuid16, local_name, mac)
                        break
                    elif comp_id in [0x67DD, 0xE02F, 0xF79F] and data_len in [0x11, 0x2A]:
                        # Govee H5183
                        sensor_data = parse_govee(self, man_spec_data, service_class_uuid16, local_name, mac)
                    elif comp_id in [0x5112, 0x5122, 0x6111, 0x6121] and data_len == 0x0f:
                        # Air Mentor 2S
                        sensor_data = parse_airmentor(self, man_spec_data, mac)
                        break
                    elif comp_id == 0x8801 and data_len in [0x0C, 0x25]:
                        # Govee H5179
                        sensor_data = parse_govee(self, man_spec_data, service_class_uuid16, local_name, mac)
                        break
                    elif comp_id == 0xAA55 and data_len == 0x14:
                        # Thermobeacon
                        sensor_data = parse_thermobeacon(self, man_spec_data, mac)
                        break
                    elif comp_id == 0xEA1C and data_len == 0x17:
                        # Govee H50555
                        sensor_data = parse_govee(self, man_spec_data, service_class_uuid16, local_name, mac)
                        break
                    elif comp_id == 0xEC88 and data_len in [0x09, 0x0A, 0x0C, 0x22, 0x24, 0x25]:
                        # Govee H5051/H5071/H5072/H5075/H5074
                        sensor_data = parse_govee(self, man_spec_data, service_class_uuid16, local_name, mac)
                        break
                    elif comp_id == 0xF214 and data_len == 0x16:
                        # Grundfos
                        sensor_data = parse_grundfos(self, man_spec_data, mac)
                        break
                    elif comp_id == 0xFFFF and data_len == 0x1E:
                        # Kegtron
                        sensor_data = parse_kegtron(self, man_spec_data, mac)
                        break
                    elif comp_id == 0xA0AC and data_len == 0x0F and man_spec_data[14] in [0x06, 0x0D]:
                        # Laica
                        sensor_data = parse_laica(self, man_spec_data, mac)
                        break
                    elif comp_id == 0x0100 and data_len == 0x14:
                        # Senssun IF_B7
                        sensor_data = parse_senssun(self, man_spec_data, mac)
                        break
                    elif comp_id == 0x061A:
                        # R.W. Beckett heating systems
                        sensor_data = parse_beckett(self, man_spec_data, mac)
                        break
                    # Filter on part of the UUID16
                    elif man_spec_data[2] == 0xC0 and data_len == 0x10:
                        # Xiaogui Scale
                        sensor_data = parse_xiaogui(self, man_spec_data, mac)
                        break
                    elif man_spec_data[3] == 0x82 and data_len == 0x0E:
                        # iNode
                        sensor_data = parse_inode(self, man_spec_data, mac)
                        break
                    elif man_spec_data[3] in [
                        0x91, 0x92, 0x93, 0x94, 0x95, 0x96, 0x9A, 0x9B, 0x9C, 0x9D
                    ] and data_len == 0x19:
                        # iNode Care Sensors
                        sensor_data = parse_inode(self, man_spec_data, mac)
                        break

                    # Filter on service class uuid16
                    elif service_class_uuid16 == 0x20AA and data_len == 0x0E:
                        # Jinou BEC07-5
                        sensor_data = parse_jinou(self, man_spec_data, mac)
                        break
                    elif service_class_uuid16 in [0x5182, 0x5184] and data_len in [0x14, 0x2D]:
                        # Govee H5182 and H5184
                        sensor_data = parse_govee(self, man_spec_data, service_class_uuid16, local_name, mac)
                        break
                    elif service_class_uuid16 == 0x5183 and data_len in [0x11, 0x2A]:
                        # Govee H5183
                        sensor_data = parse_govee(self, man_spec_data, service_class_uuid16, local_name, mac)
                        break
                    elif service_class_uuid16 in [0x5185, 0x5198] and data_len in [0x17, 0x30]:
                        # Govee H5185 and H5198
                        sensor_data = parse_govee(self, man_spec_data, service_class_uuid16, local_name, mac)
                        break
                    elif service_class_uuid16 == 0xF0FF:
                        if comp_id in [0x0010, 0x0011, 0x0015, 0x0018, 0x001B] and data_len in [0x15, 0x17]:
                            # Thermobeacon
                            sensor_data = parse_thermobeacon(self, man_spec_data, mac)
                            break
                        elif (comp_id in [0x0000, 0x0001] or local_name in ["iBBQ", "xBBQ", "sps", "tps"]) and (
                            data_len in [0x0A, 0x0D, 0x0F, 0x13, 0x17]
                        ):
                            # Inkbird
                            sensor_data = parse_inkbird(self, man_spec_data, local_name, mac)
                            break
                        else:
                            unknown_sensor = True

                    # Filter on service class uuid128
                    elif service_class_uuid128 == (
                        b'\xb0\x0a\x09\xec\xd7\x9d\xb8\x93\xba\x42\xd6\x11\x00\x00\x09\xef'
                    ) and data_len in [0x06, 0x08]:
                        # Sensorpush
                        sensor_data = parse_sensorpush(self, man_spec_data, mac)
                        break

                    # Filter on complete local name
                    elif local_name in ["sps", "tps"] and data_len == 0x0A:
                        # Inkbird IBS-TH
                        sensor_data = parse_inkbird(self, man_spec_data, local_name, mac)
                        break
                    elif local_name[0:5] in ["TP357", "TP359"] and data_len >= 0x07:
                        # Thermopro
                        sensor_data = parse_thermopro(self, man_spec_data, local_name[0:5], mac)
                        break

                    # Filter on other parts of the manufacturer specific data
                    elif data_len == 0x1B and ((man_spec_data[4] << 8) | man_spec_data[5]) == 0xBEAC:
                        # AltBeacon
                        sensor_data, tracker_data = parse_altbeacon(self, man_spec_data, comp_id, mac)
                        uuid = man_spec_data[6:22]
                        break

                    elif man_spec_data[0] == 0x12 and comp_id == 0xACC0:  # Acconeer
                        sensor_data = parse_acconeer(self, man_spec_data, mac)
                        break
                    else:
                        unknown_sensor = True
            else:
                unknown_sensor = True
            if unknown_sensor and self.report_unknown == "Other":
                _LOGGER.info(
                    "Unknown advertisement received for mac: %s"
                    "service data: %s"
                    "manufacturer specific data: %s"
                    "local name: %s"
                    "UUID16: %s,"
                    "UUID128: %s",
                    to_mac(mac),
                    service_data_list,
                    man_spec_data_list,
                    local_name,
                    service_class_uuid16,
                    service_class_uuid128,
                )
            break

        # Ignore sensor data for MAC addresses not in sensor whitelist, when discovery is disabled
        if self.discovery is False and mac not in self.sensor_whitelist:
            _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(mac))
            sensor_data = None
        # Ignore sensor data for UUID not in sensor whitelist, when discovery is disabled
        if self.discovery is False and uuid and uuid not in self.sensor_whitelist:
            _LOGGER.debug("Discovery is disabled. UUID: %s is not whitelisted!", to_uuid(uuid))

            sensor_data = None
        # add rssi and local name to the sensor_data output
        if sensor_data:
            sensor_data.update({
                "rssi": rssi,
                "local_name": local_name,
            })
        else:
            sensor_data = None

        # check for monitored device trackers
        tracker_id = tracker_data['tracker_id'] if tracker_data and 'tracker_id' in tracker_data else mac
        if tracker_id in self.tracker_whitelist:
            tracker_data.update({
                "is connected": True,
                "mac": to_unformatted_mac(mac),
                "rssi": rssi,
                "local_name": local_name,
            })
        else:
            tracker_data = None

        if self.report_unknown_whitelist:
            if tracker_id in self.report_unknown_whitelist:
                _LOGGER.info(
                    "BLE advertisement received from MAC/UUID %s: "
                    "service data: %s"
                    "manufacturer specific data: %s"
                    "local name: %s"
                    "UUID16: %s,"
                    "UUID128: %s",
                    tracker_id.hex(),
                    service_data_list,
                    man_spec_data_list,
                    local_name,
                    service_class_uuid16,
                    service_class_uuid128
                )

        return sensor_data, tracker_data
