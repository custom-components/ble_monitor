# Parser for Xiaomi MiBeacon BLE advertisements
import logging
import math
import struct
from Cryptodome.Cipher import AES

_LOGGER = logging.getLogger(__name__)

# Sensors type dictionary
# {device type code: (device name, binary?)}
XIAOMI_TYPE_DICT = {
    b'\xAA\x01': ("LYWSDCGQ", False),
    b'\x47\x03': ("CGG1", False),
    b'\x48\x0B': ("CGG1-ENCRYPTED", False),
    b'\x6F\x06': ("CGDK2", False),
    b'\x5B\x04': ("LYWSD02", False),
    b'\x5B\x05': ("LYWSD03MMC", False),
    b'\x76\x05': ("CGD1", False),
    b'\xd3\x06': ("MHO-C303", False),
    b'\x87\x03': ("MHO-C401", False),
    b'\xDF\x02': ("JQJCY01YM", False),
    b'\x98\x00': ("HHCCJCY01", False),
    b'\xBC\x03': ("GCLS002", False),
    b'\x5D\x01': ("HHCCPOT002", False),
    b'\x0A\x04': ("WX08ZM", True),
    b'\x8B\x09': ("MCCGQ02HL", True),
    b'\xD6\x03': ("CGH1", True),
    b'\x83\x00': ("YM-K1501", True),
    b'\x13\x01': ("YM-K1501EU", True),
    b'\x5C\x04': ("V-SK152", True),
    b'\x63\x08': ("SJWS01LM", True),
    b'\xF6\x07': ("MJYD02YL", True),
    b'\xDD\x03': ("MUE4094RT", True),
    b'\x8D\x0A': ("RTCGQ02LM", True),
    b'\x83\x0A': ("CGPR1", True),
    b'\xDB\x00': ("MMC-T201-1", False),
    b'\x89\x04': ("M1S-T500", False),
    b'\xBF\x07': ("YLAI003", False),
    b'\x53\x01': ("YLYK01YL", True),
    b'\xB6\x03': ("YLKG07YL/YLKG08YL", False),
}

# List of devices with legacy MiBeacon V2/V3 decryption
LEGACY_DECRYPT_LIST = ["YLYK01YL", "YLKG07YL/YLKG08YL"]

# Structured objects for data conversions
TH_STRUCT = struct.Struct("<hH")
H_STRUCT = struct.Struct("<H")
T_STRUCT = struct.Struct("<h")
TTB_STRUCT = struct.Struct("<hhB")
CND_STRUCT = struct.Struct("<H")
ILL_STRUCT = struct.Struct("<I")
LIGHT_STRUCT = struct.Struct("<I")
FMDH_STRUCT = struct.Struct("<H")
M_STRUCT = struct.Struct("<L")
P_STRUCT = struct.Struct("<H")
BUTTON_STRUCT = struct.Struct("<BBB")


# Advertisement conversion of measurement data
# https://iot.mi.com/new/doc/embedded-development/ble/object-definition
def obj0300(xobj):
    return {"motion": xobj[0], "motion timer": xobj[0]}


def obj1000(xobj):
    return {"toothbrush mode": xobj[1]}


def obj0f00(xobj):
    if len(xobj) == 3:
        (value,) = LIGHT_STRUCT.unpack(xobj + b'\x00')
        # MJYD02YL:  1 - moving no light, 100 - moving with light
        # RTCGQ02LM: 0 - moving no light, 256 - moving with light
        # CGPR1:     moving, value is illumination in lux
        return {"motion": 1, "motion timer": 1, "light": int(value >= 100), "illuminance": value}
    else:
        return {}


def obj0110(xobj):
    (button, value, press) = BUTTON_STRUCT.unpack(xobj)

    # remote command and remote binary
    if button == 0:
        remote_command = "on"
        remote_binary = 1
    elif button == 1:
        remote_command = "off"
        remote_binary = 0
    elif button == 2:
        remote_command = "sun"
        remote_binary = None
    elif button == 3:
        remote_command = "+"
        remote_binary = 1
    elif button == 4:
        remote_command = "m"
        remote_binary = None
    elif button == 5:
        remote_command = "-"
        remote_binary = 1
    else:
        remote_command = "unknown command"
        remote_binary = None

    # press type and dimmer
    if press == 0:
        press_type = "single press"
        dimmer = None
    elif press == 1:
        press_type = "double press"
        dimmer = None
    elif press == 2:
        press_type = "long press"
        dimmer = None
    elif press == 3:
        if button == 0:
            press_type = "short press"
            dimmer = str(value) + " x"
        if button == 1:
            press_type = "long press"
            dimmer = str(value) + " seconds"
    elif press == 4:
        if button == 0:
            if value <= 127:
                press_type = "rotate right"
                dimmer = str(value) + " step(s)"
            else:
                press_type = "rotate left"
                dimmer = str(256 - value) + " step(s)"
        elif button <= 127:
            press_type = "rotate right (pressed)"
            dimmer = str(button) + " step(s)"
        else:
            press_type = "rotate left (pressed)"
            dimmer = str(256 - button) + " step(s)"
    else:
        press_type = "no press"
        dimmer = None

    if remote_binary is None:
        return {"remote": remote_command, "press": press_type, "dimmer": dimmer}
    else:
        return {"remote": remote_command, "press": press_type, "remote binary": remote_binary, "dimmer": dimmer}


def obj0410(xobj):
    if len(xobj) == 2:
        (temp,) = T_STRUCT.unpack(xobj)
        return {"temperature": temp / 10}
    else:
        return {}


def obj0510(xobj):
    return {"switch": xobj[0], "temperature": xobj[1]}


def obj0610(xobj):
    if len(xobj) == 2:
        (humi,) = H_STRUCT.unpack(xobj)
        return {"humidity": humi / 10}
    else:
        return {}


def obj0710(xobj):
    if len(xobj) == 3:
        (illum,) = ILL_STRUCT.unpack(xobj + b'\x00')
        return {"illuminance": illum, "light": 1 if illum == 100 else 0}
    else:
        return {}


def obj0810(xobj):
    return {"moisture": xobj[0]}


def obj0910(xobj):
    if len(xobj) == 2:
        (cond,) = CND_STRUCT.unpack(xobj)
        return {"conductivity": cond}
    else:
        return {}


def obj1010(xobj):
    if len(xobj) == 2:
        (fmdh,) = FMDH_STRUCT.unpack(xobj)
        return {"formaldehyde": fmdh / 100}
    else:
        return {}


def obj1210(xobj):
    return {"switch": xobj[0]}


def obj1310(xobj):
    return {"consumable": xobj[0]}


def obj1410(xobj):
    return {"moisture": xobj[0]}


def obj1710(xobj):
    if len(xobj) == 4:
        (motion,) = M_STRUCT.unpack(xobj)
        # seconds since last motion detected message (not used, we use motion timer in obj0f00)
        # 0 = motion detected
        return {"motion": 1 if motion == 0 else 0}
    else:
        return {}


def obj1810(xobj):
    return {"light": xobj[0]}


def obj1910(xobj):
    return {"opening": xobj[0]}


def obj0a10(xobj):
    batt = xobj[0]
    volt = 2.2 + (3.1 - 2.2) * (batt / 100)
    return {"battery": batt, "voltage": volt}


def obj0d10(xobj):
    if len(xobj) == 4:
        (temp, humi) = TH_STRUCT.unpack(xobj)
        return {"temperature": temp / 10, "humidity": humi / 10}
    else:
        return {}


def obj0020(xobj):
    if len(xobj) == 5:
        (temp1, temp2, bat) = TTB_STRUCT.unpack(xobj)
        # Body temperature is calculated from the two measured temperatures.
        # Formula is based on approximation based on values inthe app in the range 36.5 - 37.8.
        body_temp = (
            3.71934 * pow(10, -11) * math.exp(0.69314 * temp1 / 100)
            - 1.02801 * pow(10, -8) * math.exp(0.53871 * temp2 / 100)
            + 36.413
        )
        return {"temperature": body_temp, "battery": bat}
    else:
        return {}


# Dataobject dictionary
# {dataObject_id: (converter, binary, measuring)
xiaomi_dataobject_dict = {
    b'\x03\x00': (obj0300, True, False),
    b'\x10\x00': (obj1000, False, True),
    b'\x0F\x00': (obj0f00, True, True),
    b'\x01\x10': (obj0110, True, True),
    b'\x04\x10': (obj0410, False, True),
    b'\x05\x10': (obj0510, True, True),
    b'\x06\x10': (obj0610, False, True),
    b'\x07\x10': (obj0710, True, True),
    b'\x08\x10': (obj0810, False, True),
    b'\x09\x10': (obj0910, False, True),
    b'\x10\x10': (obj1010, False, True),
    b'\x12\x10': (obj1210, True, False),
    b'\x13\x10': (obj1310, False, True),
    b'\x14\x10': (obj1410, True, False),
    b'\x17\x10': (obj1710, True, False),
    b'\x18\x10': (obj1810, True, False),
    b'\x19\x10': (obj1910, True, False),
    b'\x0A\x10': (obj0a10, True, True),
    b'\x0D\x10': (obj0d10, False, True),
    b'\x00\x20': (obj0020, False, True),
}


def parse_xiaomi(self, data, xiaomi_index, is_ext_packet):
    # parse BLE message in Xiaomi MiBeacon format
    try:
        firmware = "Xiaomi (MiBeacon)"
        self.is_ext_packet = is_ext_packet
        # check for no BR/EDR + LE General discoverable mode flags
        advert_start = 29 if self.is_ext_packet else 14
        adv_index = data.find(b"\x02\x01\x06", advert_start, 3 + advert_start)
        adv_index2 = data.find(b"\x14\x16\x95", advert_start, 3 + advert_start)
        adv_index3 = data.find(b"\x15\x16\x95", advert_start, 3 + advert_start)
        adv_index4 = data.find(b"\x18\x16\x95", advert_start, 3 + advert_start)
        if adv_index == -1 and adv_index2 == -1 and adv_index3 == -1 and adv_index4 == -1:
            raise NoValidError("Invalid index")
        if adv_index2 != -1:
            adv_index = adv_index2
        elif adv_index3 != -1:
            adv_index = adv_index3
        elif adv_index4 != -1:
            adv_index = adv_index4

        # check for BTLE msg size
        self.msg_length = data[2] + 3
        if self.msg_length != len(data):
            raise NoValidError("Invalid msg size")

        # extract device type
        self.device_type = data[xiaomi_index + 5:xiaomi_index + 7]

        # extract frame control bits
        self.framectrl_data = data[xiaomi_index + 3:xiaomi_index + 5]
        framectrl, = struct.unpack('>H', self.framectrl_data)

        # flag advertisements without mac address in service data
        if self.device_type == b'\xF6\x07' and self.framectrl_data == b'\x48\x59':
            # MJYD02YL does not have a MAC address in the service data of some advertisements
            mac_in_service_data = False
        elif self.device_type == b'\xDD\x03' and self.framectrl_data == b'\x40\x30':
            # MUE4094RT does not have a MAC address in the service data
            mac_in_service_data = False
        else:
            mac_in_service_data = True

        # check for MAC presence in message and in service data
        mac_index = adv_index - 14 if self.is_ext_packet else adv_index
        if mac_in_service_data is True:
            self.xiaomi_mac_reversed = data[xiaomi_index + 8:xiaomi_index + 14]
            source_mac_reversed = data[mac_index - 7:mac_index - 1]
            if self.xiaomi_mac_reversed != source_mac_reversed:
                raise NoValidError("Invalid MAC address")
        else:
            # for sensors without mac in service data, use the first mac in advertisment
            self.xiaomi_mac_reversed = data[mac_index - 7:mac_index - 1]

        # check for MAC presence in whitelist, if needed
        if self.discovery is False and self.xiaomi_mac_reversed not in self.whitelist:
            return None, None, None
        self.packet_id = data[xiaomi_index + 7]
        try:
            prev_packet = self.lpacket_ids[self.xiaomi_mac_reversed]
        except KeyError:
            # start with empty first packet
            prev_packet = None, None, None
        if prev_packet == self.packet_id:
            # only process new messages
            return None, None, None
        self.lpacket_ids[self.xiaomi_mac_reversed] = self.packet_id

        # extract RSSI byte
        rssi_index = 18 if self.is_ext_packet else self.msg_length - 1
        (rssi,) = struct.unpack("<b", data[rssi_index:rssi_index + 1])

        # strange positive RSSI workaround
        if rssi > 0:
            rssi = -rssi
        try:
            sensor_type, binary_data = XIAOMI_TYPE_DICT[self.device_type]
        except KeyError:
            if self.report_unknown == "Xiaomi":
                _LOGGER.info(
                    "BLE ADV from UNKNOWN Xiaomi sensor: RSSI: %s, MAC: %s, ADV: %s",
                    rssi,
                    ''.join('{:02X}'.format(x) for x in self.xiaomi_mac_reversed[::-1]),
                    data.hex()
                )
            raise NoValidError("Device unkown")

        # check data is present
        if not (framectrl & 0x4000):
            return {
                "rssi": rssi,
                "mac": ''.join('{:02X}'.format(x) for x in self.xiaomi_mac_reversed[::-1]),
                "type": sensor_type,
                "packet": self.packet_id,
                "firmware": firmware,
                "data": False,
            }, None, None
        self.xdata_length = 0
        self.xdata_point = 0

        # check capability byte present
        if framectrl & 0x2000:
            self.xdata_length = -1
            self.xdata_point = 1

        # check for messages without mac address in service data
        if mac_in_service_data is False:
            self.xdata_length = +6
            self.xdata_point = -6

        # parse_xiaomi data length = message length
        #     -all bytes before XiaomiUUID
        #     -3 bytes Xiaomi UUID + ADtype
        #     -1 byte rssi
        #     -3+1 bytes sensor type
        #     -1 byte packet_id
        #     -6 bytes MAC (if present)
        #     -capability byte offset
        self.xdata_length += self.msg_length - xiaomi_index - 15
        if self.xdata_length < 3:
            raise NoValidError("Xdata length invalid")

        self.xdata_point += xiaomi_index + 14

        # check if parse_xiaomi data start and length is valid
        if self.xdata_length != len(data[self.xdata_point:-1]):
            raise NoValidError("Invalid data length")

        # decryption of encrypted messages
        if framectrl & 0x0800:
            encrypted_length = len(data)
            if sensor_type in LEGACY_DECRYPT_LIST:
                firmware = "Xiaomi (MiBeacon V2/V3 encrypted)"
                data = decrypt_mibeacon_legacy(self, data)
            else:
                firmware = "Xiaomi (MiBeacon V4/V5 encrypted)"
                data = decrypt_mibeacon_v4_v5(self, data)
            if data is None:
                raise NoValidError("Data decryption failed")
            decrypted_length = len(data)
            self.msg_length = self.msg_length - encrypted_length + decrypted_length

        result = {
            "rssi": rssi,
            "mac": ''.join('{:02X}'.format(x) for x in self.xiaomi_mac_reversed[::-1]),
            "type": sensor_type,
            "packet": self.packet_id,
            "firmware": firmware,
            "data": True,
        }
        binary = False
        measuring = False

        # loop through parse_xiaomi payload
        # assume that the data may have several values of different types
        while True:
            xvalue_typecode = data[self.xdata_point:self.xdata_point + 2]
            try:
                xvalue_length = data[self.xdata_point + 2]
            except ValueError as error:
                _LOGGER.error("xvalue_length conv. error: %s", error)
                _LOGGER.error("xdata_point: %s", self.xdata_point)
                _LOGGER.error("data: %s", data.hex())
                result = {}
                break
            except IndexError as error:
                _LOGGER.error("Wrong xdata_point: %s", error)
                _LOGGER.error("xdata_point: %s", self.xdata_point)
                _LOGGER.error("data: %s", data.hex())
                result = {}
                break

            xnext_point = self.xdata_point + 3 + xvalue_length
            xvalue = data[self.xdata_point + 3:xnext_point]
            resfunc, tbinary, tmeasuring = xiaomi_dataobject_dict.get(xvalue_typecode, (None, None, None))

            if resfunc:
                binary = binary or tbinary
                measuring = measuring or tmeasuring
                result.update(resfunc(xvalue))
            else:
                if self.report_unknown == "Xiaomi":
                    _LOGGER.info(
                        "UNKNOWN dataobject from Xiaomi DEVICE: %s, MAC: %s, ADV: %s",
                        sensor_type,
                        ''.join('{:02X}'.format(x) for x in self.xiaomi_mac_reversed[::-1]),
                        data.hex()
                    )

            if xnext_point > self.msg_length - 3:
                break
            self.xdata_point = xnext_point

        binary = binary and binary_data
        return result, binary, measuring

    except NoValidError as nve:
        _LOGGER.debug("Invalid data: %s", nve)

    return None, None, None


def decrypt_mibeacon_v4_v5(self, data):
    try:
        # check for minimum length of encrypted advertisement
        if self.xdata_length < 11:
            raise DecryptionError("Invalid encrypted data length")
        # try to find encryption key for current device
        try:
            key = self.aeskeys[self.xiaomi_mac_reversed]
            if len(key) != 16:
                raise DecryptionError("Encryption key should be 16 bytes (32 characters) long")
        except KeyError:
            # no encryption key found
            raise DecryptionError("No encryption key found")
        endoffset = self.msg_length - int(not self.is_ext_packet)
        encrypted_payload = data[self.xdata_point:endoffset]
        payload_counter = b"".join([bytes([self.packet_id]), encrypted_payload[-7:-4]])
        nonce = b"".join(
            [
                self.xiaomi_mac_reversed,
                self.device_type,
                payload_counter
            ]
        )

        aad = b"\x11"
        token = encrypted_payload[-4:]
        cipherpayload = encrypted_payload[:-7]
        cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
        cipher.update(aad)

        try:
            decrypted_payload = cipher.decrypt_and_verify(cipherpayload, token)
        except ValueError as error:
            _LOGGER.error("Decryption failed: %s", error)
            _LOGGER.error("token: %s", token.hex())
            _LOGGER.error("nonce: %s", nonce.hex())
            _LOGGER.error("encrypted_payload: %s", encrypted_payload.hex())
            _LOGGER.error("cipherpayload: %s", cipherpayload.hex())
            raise DecryptionError("Error decrypting with arguments")
        if decrypted_payload is None:
            _LOGGER.error(
                "Decryption failed for %s, decrypted payload is None",
                "".join("{:02X}".format(x) for x in self.xiaomi_mac_reversed[::-1]),
            )
            raise DecryptionError("Decrypted payload is empty")

        # replace cipher with decrypted data
        if self.is_ext_packet:
            decrypted_data = b"".join((data[:self.xdata_point], decrypted_payload))
        else:
            decrypted_data = b"".join((data[:self.xdata_point], decrypted_payload, data[-1:]))

        return decrypted_data

    except DecryptionError as nve:
        _LOGGER.error("Decryption MiBeacon V4/V5 advertisement failed: %s", nve)
        return None


def decrypt_mibeacon_legacy(self, data):
    try:
        # check for minimum length of encrypted advertisement
        if self.xdata_length < 9:
            raise DecryptionError("Invalid encrypted data length")
        # try to find encryption key for current device
        try:
            aeskey = self.aeskeys[self.xiaomi_mac_reversed]
            if len(aeskey) != 12:
                raise DecryptionError("encryption key should be 12 bytes (24 characters) long")
            key = b"".join([aeskey[0:6], bytes.fromhex("8d3d3c97"), aeskey[6:]])
        except KeyError:
            # no encryption key found
            raise DecryptionError("No encryption key found")
        endoffset = self.msg_length - int(not self.is_ext_packet)
        encrypted_payload = data[self.xdata_point:endoffset]
        payload_counter = b"".join([bytes([self.packet_id]), encrypted_payload[-4:-1]])
        nonce = b"".join(
            [
                self.framectrl_data,
                self.device_type,
                payload_counter,
                self.xiaomi_mac_reversed[:-1]
            ]
        )

        aad = b"\x11"
        cipherpayload = encrypted_payload[:-4]
        cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
        cipher.update(aad)

        try:
            decrypted_payload = cipher.decrypt(cipherpayload)
        except ValueError as error:
            _LOGGER.error("Decryption failed: %s", error)
            _LOGGER.error("nonce: %s", nonce.hex())
            _LOGGER.error("encrypted_payload: %s", encrypted_payload.hex())
            _LOGGER.error("cipherpayload: %s", cipherpayload.hex())
            raise DecryptionError("Error decrypting with arguments")
        if decrypted_payload is None:
            _LOGGER.error(
                "Decryption failed for %s, decrypted payload is None",
                "".join("{:02X}".format(x) for x in self.xiaomi_mac_reversed[::-1]),
            )
            raise DecryptionError("Decrypted payload is empty")

        # replace cipher with decrypted data
        if self.is_ext_packet:
            decrypted_data = b"".join((data[:self.xdata_point], decrypted_payload))
        else:
            decrypted_data = b"".join((data[:self.xdata_point], decrypted_payload, data[-1:]))

        return decrypted_data

    except DecryptionError as nve:
        _LOGGER.error("Decryption MiBeacon V2/V3 advertisement failed: %s", nve)
        return None


class XiaomiMiBeaconParser:
    """Class defining the content of an advertisement of a Xiaomi MiBeacon sensor."""

    def decode(self, data, xiaomi_index, is_ext_packet):
        # Decode Xiaomi MiBeacon advertisement
        result = parse_xiaomi(self, data, xiaomi_index, is_ext_packet)
        return result


class NoValidError(Exception):
    pass


class DecryptionError(Exception):
    pass
