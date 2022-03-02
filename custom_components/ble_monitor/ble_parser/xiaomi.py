"""Parser for Xiaomi MiBeacon BLE advertisements"""
import logging
import math
import struct
from Cryptodome.Cipher import AES

from homeassistant.util import datetime

_LOGGER = logging.getLogger(__name__)

# Device type dictionary
# {device type code: device name}
XIAOMI_TYPE_DICT = {
    0x01AA: "LYWSDCGQ",
    0x045B: "LYWSD02",
    0x055B: "LYWSD03MMC",
    0x1203: "XMWSDJ04MMC",
    0x04E1: "XMMF01JQD",
    0x0098: "HHCCJCY01",
    0x03BC: "GCLS002",
    0x015D: "HHCCPOT002",
    0x040A: "WX08ZM",
    0x098B: "MCCGQ02HL",
    0x0083: "YM-K1501",
    0x0113: "YM-K1501EU",
    0x045C: "V-SK152",
    0x0863: "SJWS01LM",
    0x07F6: "MJYD02YL",
    0x03DD: "MUE4094RT",
    0x0A8D: "RTCGQ02LM",
    0x00DB: "MMC-T201-1",
    0x0489: "M1S-T500",
    0x0C3C: "CGC1",
    0x0576: "CGD1",
    0x066F: "CGDK2",
    0x0347: "CGG1",
    0x0B48: "CGG1-ENCRYPTED",
    0x03D6: "CGH1",
    0x0A83: "CGPR1",
    0x06d3: "MHO-C303",
    0x0387: "MHO-C401",
    0x02DF: "JQJCY01YM",
    0x0997: "JTYJGD03MI",
    0x1568: "K9B-1BTN",
    0x1569: "K9B-2BTN",
    0x0DFD: "K9B-3BTN",
    0x07BF: "YLAI003",
    0x0153: "YLYK01YL",
    0x068E: "YLYK01YL-FANCL",
    0x04E6: "YLYK01YL-VENFAN",
    0x03BF: "YLYB01YL-BHFRC",
    0x03B6: "YLKG07YL/YLKG08YL",
    0x069E: "ZNMS16LM",
    0x069F: "ZNMS17LM",
    0x04E9: "MJZNMSQ01YD",
    0x098C: "XMZNMST02YD",
}

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
FLOAT_STRUCT = struct.Struct("<f")

# Definition of lock messages
BLE_LOCK_ERROR = {
    0xC0DE0000: "frequent unlocking with incorrect password",
    0xC0DE0001: "frequent unlocking with wrong fingerprints",
    0xC0DE0002: "operation timeout (password input timeout)",
    0xC0DE0003: "lock picking",
    0xC0DE0004: "reset button is pressed",
    0xC0DE0005: "the wrong key is frequently unlocked",
    0xC0DE0006: "foreign body in the keyhole",
    0xC0DE0007: "the key has not been taken out",
    0xC0DE0008: "error NFC frequently unlocks",
    0xC0DE0009: "timeout is not locked as required",
    0xC0DE000A: "failure to unlock frequently in multiple ways",
    0xC0DE000B: "unlocking the face frequently fails",
    0xC0DE000C: "failure to unlock the vein frequently",
    0xC0DE000D: "hijacking alarm",
    0xC0DE000E: "unlock inside the door after arming",
    0xC0DE000F: "palmprints frequently fail to unlock",
    0xC0DE0010: "the safe was moved",
    0xC0DE1000: "the battery level is less than 10%",
    0xC0DE1001: "the battery is less than 5%",
    0xC0DE1002: "the fingerprint sensor is abnormal",
    0xC0DE1003: "the accessory battery is low",
    0xC0DE1004: "mechanical failure",
    0xC0DE1005: "the lock sensor is faulty",
}

BLE_LOCK_ACTION = {
    0b0000: [0, "unlock outside the door"],
    0b0001: [1, "lock"],
    0b0010: [1, "turn on anti-lock"],
    0b0011: [0, "turn off anti-lock"],
    0b0100: [0, "unlock inside the door"],
    0b0101: [1, "lock inside the door"],
    0b0110: [1, "turn on child lock"],
    0b0111: [0, "turn off child lock"],
    0b1000: [1, "lock outside the door"],
    0b1111: [0, "abnormal"],
}

BLE_LOCK_METHOD = {
    0b0000: "bluetooth",
    0b0001: "password",
    0b0010: "biometrics",
    0b0011: "key",
    0b0100: "turntable",
    0b0101: "nfc",
    0b0110: "one-time password",
    0b0111: "two-step verification",
    0b1001: "Homekit",
    0b1000: "coercion",
    0b1010: "manual",
    0b1011: "automatic",
    0b1111: "abnormal"
}


# Advertisement conversion of measurement data
# https://iot.mi.com/new/doc/embedded-development/ble/object-definition
def obj0003(xobj):
    # Motion
    return {"motion": xobj[0], "motion timer": xobj[0]}


def obj0006(xobj):
    # Fingerprint
    if len(xobj) == 5:
        key_id = xobj[0:4]
        match_byte = xobj[4]
        if key_id == b'\x00\x00\x00\x00':
            key_id = "administrator"
        elif key_id == b'\xff\xff\xff\xff':
            key_id = "unknown operator"
        else:
            key_id = int.from_bytes(key_id, 'little')
        if match_byte == 0x00:
            result = "match successful"
        elif match_byte == 0x01:
            result = "match failed"
        elif match_byte == 0x02:
            result = "timeout"
        elif match_byte == 0x033:
            result = "low quality (too light, fuzzy)"
        elif match_byte == 0x04:
            result = "insufficient area"
        elif match_byte == 0x05:
            result = "skin is too dry"
        elif match_byte == 0x06:
            result = "skin is too wet"
        else:
            result = None

        fingerprint = 1 if match_byte == 0x00 else 0

        return {
            "fingerprint": fingerprint,
            "result": result,
            "key id": key_id,
        }
    else:
        return {}


def obj0010(xobj):
    # Toothbrush
    if xobj[0] == 0:
        return {'toothbrush': 1, 'counter': xobj[1]}
    else:
        return {'toothbrush': 0, 'score': xobj[1]}


def obj000b(xobj):
    # Lock
    if len(xobj) == 9:
        action = xobj[0] & 0x0F
        method = xobj[0] >> 4
        key_id = int.from_bytes(xobj[1:5], 'little')
        timestamp = int.from_bytes(xobj[5:], 'little')

        timestamp = datetime.fromtimestamp(timestamp).isoformat()

        # all keys except Bluetooth have only 65536 values
        error = BLE_LOCK_ERROR.get(key_id)
        if error is None and method > 0:
            key_id &= 0xFFFF
        elif error:
            key_id = hex(key_id)

        if action not in BLE_LOCK_ACTION or method not in BLE_LOCK_METHOD:
            return {}

        lock = BLE_LOCK_ACTION[action][0]
        action = BLE_LOCK_ACTION[action][1]
        method = BLE_LOCK_METHOD[method]

        return {
            "lock": lock,
            "action": action,
            "method": method,
            "error": error,
            "key id": key_id,
            "timestamp": timestamp,
        }
    else:
        return {}


def obj000f(xobj, device_type):
    # Moving with light
    if len(xobj) == 3:
        (value,) = LIGHT_STRUCT.unpack(xobj + b'\x00')

        if device_type in ["MJYD02YL", "RTCGQ02LM"]:
            # MJYD02YL:  1 - moving no light, 100 - moving with light
            # RTCGQ02LM: 0 - moving no light, 256 - moving with light
            return {"motion": 1, "motion timer": 1, "light": int(value >= 100)}
        elif device_type == "CGPR1":
            # CGPR1:     moving, value is illumination in lux
            return {"motion": 1, "motion timer": 1, "illuminance": value, "light": int(value >= 100)}
        else:
            return {}
    else:
        return {}


def obj1001(xobj, device_type):
    if len(xobj) == 3:
        (button_type, value, press) = BUTTON_STRUCT.unpack(xobj)

        # remote command and remote binary
        remote_command = None
        fan_remote_command = None
        ven_fan_remote_command = None
        bathroom_remote_command = None
        one_btn_switch = None
        two_btn_switch_left = None
        two_btn_switch_right = None
        three_btn_switch_left = None
        three_btn_switch_middle = None
        three_btn_switch_right = None
        cube_direction = None
        remote_binary = None

        if button_type == 0:
            remote_command = "on"
            fan_remote_command = "fan toggle"
            ven_fan_remote_command = "swing"
            bathroom_remote_command = "stop"
            one_btn_switch = "toggle"
            two_btn_switch_left = "toggle"
            three_btn_switch_left = "toggle"
            cube_direction = "right"
            remote_binary = 1
        elif button_type == 1:
            remote_command = "off"
            fan_remote_command = "light toggle"
            ven_fan_remote_command = "power toggle"
            bathroom_remote_command = "air exchange"
            two_btn_switch_right = "toggle"
            three_btn_switch_middle = "toggle"
            cube_direction = "left"
            remote_binary = 0
        elif button_type == 2:
            remote_command = "sun"
            fan_remote_command = "wind speed"
            ven_fan_remote_command = "timer 60 minutes"
            bathroom_remote_command = "fan"
            two_btn_switch_left = "toggle"
            two_btn_switch_right = "toggle"
            three_btn_switch_right = "toggle"
            remote_binary = None
        elif button_type == 3:
            remote_command = "+"
            fan_remote_command = "color temperature"
            ven_fan_remote_command = "strong wind speed"
            bathroom_remote_command = "speed +"
            three_btn_switch_left = "toggle"
            three_btn_switch_middle = "toggle"
            remote_binary = 1
        elif button_type == 4:
            remote_command = "m"
            fan_remote_command = "wind mode"
            ven_fan_remote_command = "timer 30 minutes"
            bathroom_remote_command = "speed -"
            three_btn_switch_middle = "toggle"
            three_btn_switch_right = "toggle"
            remote_binary = None
        elif button_type == 5:
            remote_command = "-"
            fan_remote_command = "brightness"
            ven_fan_remote_command = "low wind speed"
            bathroom_remote_command = "dry"
            three_btn_switch_left = "toggle"
            three_btn_switch_right = "toggle"
            remote_binary = 1
        elif button_type == 6:
            bathroom_remote_command = "light toggle"
            three_btn_switch_left = "toggle"
            three_btn_switch_middle = "toggle"
            three_btn_switch_right = "toggle"
        elif button_type == 7:
            bathroom_remote_command = "swing"
        elif button_type == 8:
            bathroom_remote_command = "heat"

        # press type and dimmer
        button_press_type = "no press"
        btn_switch_press_type = "no press"
        dimmer = None

        if press == 0:
            button_press_type = "single press"
            btn_switch_press_type = "single press"
        elif press == 1:
            button_press_type = "double press"
            btn_switch_press_type = "long press"
        elif press == 2:
            button_press_type = "long press"
            btn_switch_press_type = "double press"
        elif press == 3:
            if button_type == 0:
                button_press_type = "short press"
                dimmer = value
            if button_type == 1:
                button_press_type = "long press"
                dimmer = value
        elif press == 4:
            if button_type == 0:
                if value <= 127:
                    button_press_type = "rotate right"
                    dimmer = value
                else:
                    button_press_type = "rotate left"
                    dimmer = 256 - value
            elif button_type <= 127:
                button_press_type = "rotate right (pressed)"
                dimmer = button_type
            else:
                button_press_type = "rotate left (pressed)"
                dimmer = 256 - button_type
        elif press == 5:
            button_press_type = "short press"
        elif press == 6:
            button_press_type = "long press"

        # return device specific output
        result = {}
        if device_type in ["RTCGQ02LM", "YLAI003", "JTYJGD03MI", "SJWS01LM"]:
            result["button"] = button_press_type
        elif device_type == "XMMF01JQD":
            result["button"] = cube_direction
        elif device_type == "YLYK01YL":
            result["remote"] = remote_command
            result["button"] = button_press_type
            if remote_binary is not None:
                if button_press_type == "single press":
                    result["remote single press"] = remote_binary
                else:
                    result["remote long press"] = remote_binary
        elif device_type == "YLYK01YL-FANRC":
            result["fan remote"] = fan_remote_command
            result["button"] = button_press_type
        elif device_type == "YLYK01YL-VENFAN":
            result["ventilator fan remote"] = ven_fan_remote_command
            result["button"] = button_press_type
        elif device_type == "YLYB01YL-BHFRC":
            result["bathroom heater remote"] = bathroom_remote_command
            result["button"] = button_press_type
        elif device_type == "YLKG07YL/YLKG08YL":
            result["dimmer"] = dimmer
            result["button"] = button_press_type
        elif device_type == "K9B-1BTN":
            result["button switch"] = btn_switch_press_type
            result["1_btn_switch"] = one_btn_switch
        elif device_type == "K9B-2BTN":
            result["button switch"] = btn_switch_press_type
            if two_btn_switch_left:
                result["2_btn_switch_left"] = two_btn_switch_left
            if two_btn_switch_right:
                result["2_btn_switch_right"] = two_btn_switch_right
        elif device_type == "K9B-3BTN":
            result["button switch"] = btn_switch_press_type
            if three_btn_switch_left:
                result["3_btn_switch_left"] = three_btn_switch_left
            if three_btn_switch_middle:
                result["3_btn_switch_middle"] = three_btn_switch_middle
            if three_btn_switch_right:
                result["3_btn_switch_right"] = three_btn_switch_right
        else:
            return None
        return result

    else:
        return None


def obj1004(xobj):
    # Temperature
    if len(xobj) == 2:
        (temp,) = T_STRUCT.unpack(xobj)
        return {"temperature": temp / 10}
    else:
        return {}


def obj1005(xobj):
    return {"switch": xobj[0], "temperature": xobj[1]}


def obj1006(xobj):
    # Humidity
    if len(xobj) == 2:
        (humi,) = H_STRUCT.unpack(xobj)
        return {"humidity": humi / 10}
    else:
        return {}


def obj1007(xobj):
    # Illuminance
    if len(xobj) == 3:
        (illum,) = ILL_STRUCT.unpack(xobj + b'\x00')
        return {"illuminance": illum, "light": 1 if illum == 100 else 0}
    else:
        return {}


def obj1008(xobj):
    # Moisture
    return {"moisture": xobj[0]}


def obj1009(xobj):
    # Conductivity
    if len(xobj) == 2:
        (cond,) = CND_STRUCT.unpack(xobj)
        return {"conductivity": cond}
    else:
        return {}


def obj1010(xobj):
    # Formaldehyde
    if len(xobj) == 2:
        (fmdh,) = FMDH_STRUCT.unpack(xobj)
        return {"formaldehyde": fmdh / 100}
    else:
        return {}


def obj1012(xobj):
    # Switch
    return {"switch": xobj[0]}


def obj1013(xobj):
    # Consumable (in percent)
    return {"consumable": xobj[0]}


def obj1014(xobj):
    # Moisture
    return {"moisture": xobj[0]}


def obj1015(xobj):
    # Smoke
    return {"smoke detector": xobj[0]}


def obj1017(xobj):
    # Motion
    if len(xobj) == 4:
        (motion,) = M_STRUCT.unpack(xobj)
        # seconds since last motion detected message (not used, we use motion timer in obj000f)
        # 0 = motion detected
        return {"motion": 1 if motion == 0 else 0}
    else:
        return {}


def obj1018(xobj):
    # Light intensity
    return {"light": xobj[0]}


def obj1019(xobj):
    # Door
    open_obj = xobj[0]
    if open_obj == 0:
        opening = 1
        status = "opened"
    elif open_obj == 1:
        opening = 0
        status = "closed"
    elif open_obj == 2:
        opening = 1
        status = "closing timeout"
    elif open_obj == 3:
        opening = 1
        status = "device reset"
    else:
        opening = 0
        status = None
    return {"opening": opening, "status": status}


def obj100a(xobj):
    # Battery
    batt = xobj[0]
    volt = 2.2 + (3.1 - 2.2) * (batt / 100)
    return {"battery": batt, "voltage": volt}


def obj100d(xobj):
    # Temperature and humidity
    if len(xobj) == 4:
        (temp, humi) = TH_STRUCT.unpack(xobj)
        return {"temperature": temp / 10, "humidity": humi / 10}
    else:
        return {}


def obj2000(xobj):
    # Body temperature
    if len(xobj) == 5:
        (temp1, temp2, bat) = TTB_STRUCT.unpack(xobj)
        # Body temperature is calculated from the two measured temperatures.
        # Formula is based on approximation based on values inthe app in the range 36.5 - 37.8.
        body_temp = (
            3.71934 * pow(10, -11) * math.exp(0.69314 * temp1 / 100) - (
                1.02801 * pow(10, -8) * math.exp(0.53871 * temp2 / 100)
            ) + 36.413
        )
        return {"temperature": body_temp, "battery": bat}
    else:
        return {}


# The following data objects are device specific. For now only added for XMWSDJ04MMC
# https://miot-spec.org/miot-spec-v2/instances?status=all
def obj4803(xobj):
    # Battery
    batt = xobj[0]
    return {"battery": batt}


def obj4c01(xobj):
    if len(xobj) == 4:
        temp = FLOAT_STRUCT.unpack(xobj)[0]
        return {"temperature": temp}
    else:
        return {}


def obj4c08(xobj):
    if len(xobj) == 4:
        humi = FLOAT_STRUCT.unpack(xobj)[0]
        return {"humidity": humi}
    else:
        return {}


# Dataobject dictionary
# {dataObject_id: (converter}
xiaomi_dataobject_dict = {
    0x0003: obj0003,
    0x0006: obj0006,
    0x0010: obj0010,
    0x000B: obj000b,
    0x000F: obj000f,
    0x1001: obj1001,
    0x1004: obj1004,
    0x1005: obj1005,
    0x1006: obj1006,
    0x1007: obj1007,
    0x1008: obj1008,
    0x1009: obj1009,
    0x1010: obj1010,
    0x1012: obj1012,
    0x1013: obj1013,
    0x1014: obj1014,
    0x1015: obj1015,
    0x1017: obj1017,
    0x1018: obj1018,
    0x1019: obj1019,
    0x100A: obj100a,
    0x100D: obj100d,
    0x2000: obj2000,
    0x4803: obj4803,
    0x4c01: obj4c01,
    0x4c08: obj4c08,
}


def parse_xiaomi(self, data, source_mac, rssi):
    """Parser for Xiaomi sensors"""
    # check for adstruc length
    i = 9  # till Frame Counter
    msg_length = len(data)
    if msg_length < i:
        _LOGGER.debug("Invalid data length (initial check), adv: %s", data.hex())
        return None

    # extract frame control bits
    frctrl = data[4] + (data[5] << 8)
    frctrl_mesh = (frctrl >> 7) & 1  # mesh device
    frctrl_version = frctrl >> 12  # version
    frctrl_auth_mode = (frctrl >> 10) & 3
    frctrl_solicited = (frctrl >> 9) & 1
    frctrl_registered = (frctrl >> 8) & 1
    frctrl_object_include = (frctrl >> 6) & 1
    frctrl_capability_include = (frctrl >> 5) & 1
    frctrl_mac_include = (frctrl >> 4) & 1  # check for MAC address in data
    frctrl_is_encrypted = (frctrl >> 3) & 1  # check for encryption being used
    frctrl_request_timing = frctrl & 1  # old version

    # Check that device is not of mesh type
    if frctrl_mesh != 0:
        _LOGGER.debug("Xiaomi device data is a mesh type device, which is not supported. Data: %s", data.hex())
        return None

    # Check that version is 2 or higher
    if frctrl_version < 2:
        _LOGGER.debug("Xiaomi device data is using old data format, which is not supported. Data: %s", data.hex())
        return None

    # Check that MAC in data is the same as the source MAC
    if frctrl_mac_include != 0:
        i += 6
        if msg_length < i:
            _LOGGER.debug("Invalid data length (in MAC check), adv: %s", data.hex())
            return None
        xiaomi_mac_reversed = data[9:15]
        xiaomi_mac = xiaomi_mac_reversed[::-1]
        if xiaomi_mac != source_mac:
            _LOGGER.debug("Xiaomi MAC address doesn't match data MAC address. Data: %s", data.hex())
            return None
    else:
        xiaomi_mac = source_mac

    # determine the device type
    device_id = data[6] + (data[7] << 8)
    try:
        device_type = XIAOMI_TYPE_DICT[device_id]
    except KeyError:
        if self.report_unknown == "Xiaomi":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Xiaomi device: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        _LOGGER.debug("Unknown Xiaomi device found. Data: %s", data.hex())
        return None

    packet_id = data[8]

    sinfo = 'MiVer: ' + str(frctrl_version)
    sinfo += ', DevID: ' + hex(device_id) + ' : ' + device_type
    sinfo += ', FnCnt: ' + str(packet_id)
    if frctrl_request_timing != 0:
        sinfo += ', Request timing'
    if frctrl_registered != 0:
        sinfo += ', Registered and bound'
    else:
        sinfo += ', Not bound'
    if frctrl_solicited != 0:
        sinfo += ', Request APP to register and bind'
    if frctrl_auth_mode == 0:
        sinfo += ', Old version certification'
    elif frctrl_auth_mode == 1:
        sinfo += ', Safety certification'
    elif frctrl_auth_mode == 2:
        sinfo += ', Standard certification'

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and xiaomi_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(xiaomi_mac))
        return None

    # check for unique packet_id and advertisement priority
    try:
        prev_packet = self.lpacket_ids[xiaomi_mac]
    except KeyError:
        # start with empty first packet
        prev_packet = None

    if device_type in ["LYWSD03MMC", "CGG1", "MHO-C401", "CGDK2"]:
        # Check for adv priority and packet_id for devices that can also send in ATC format
        adv_priority = 19
        try:
            prev_adv_priority = self.adv_priority[xiaomi_mac]
        except KeyError:
            # start with initial adv priority
            prev_adv_priority = 0
        if adv_priority > prev_adv_priority:
            # always process advertisements with a higher priority
            self.adv_priority[xiaomi_mac] = adv_priority
        elif adv_priority == prev_adv_priority:
            # only process messages with same priority that have a unique packet id
            if prev_packet == packet_id:
                if self.filter_duplicates is True:
                    return None
                else:
                    pass
            else:
                pass
        else:
            # do not process advertisements with lower priority (ATC advertisements will be used instead)
            prev_adv_priority -= 1
            self.adv_priority[xiaomi_mac] = prev_adv_priority
            return None
    else:
        if prev_packet == packet_id:
            if self.filter_duplicates is True:
                # only process messages with highest priority and messages with unique packet id
                return None
    self.lpacket_ids[xiaomi_mac] = packet_id

    # check for capability byte present
    if frctrl_capability_include != 0:
        i += 1
        if msg_length < i:
            _LOGGER.debug("Invalid data length (in capability check), adv: %s", data.hex())
            return None
        capability_types = data[i - 1]
        sinfo += ', Capability: ' + hex(capability_types)
        if (capability_types & 0x20) != 0:
            i += 1
            if msg_length < i:
                _LOGGER.debug("Invalid data length (in capability type check), adv: %s", data.hex())
                return None
            capability_io = data[i - 1]
            sinfo += ', IO: ' + hex(capability_io)

    # check that data contains object
    if frctrl_object_include != 0:
        # check for encryption
        if frctrl_is_encrypted != 0:
            sinfo += ', Encryption'
            firmware = "Xiaomi (MiBeacon V" + str(frctrl_version) + " encrypted)"
            if frctrl_version <= 3:
                payload = decrypt_mibeacon_legacy(self, data, i, xiaomi_mac)
            else:
                payload = decrypt_mibeacon_v4_v5(self, data, i, xiaomi_mac)
        else:   # No encryption
            # check minimum advertisement length with data
            firmware = "Xiaomi (MiBeacon V" + str(frctrl_version) + ")"
            sinfo += ', No encryption'
            if msg_length < i + 3:
                _LOGGER.debug("Invalid data length (in non-encrypted data), adv: %s", data.hex())
                return None
            payload = data[i:]
    else:
        # data does not contain Object
        _LOGGER.debug("Advertisement doesn't contain payload, adv: %s", data.hex())
        return None

    result = {
        "rssi": rssi,
        "mac": ''.join(f'{i:02X}' for i in xiaomi_mac),
        "type": device_type,
        "packet": packet_id,
        "firmware": firmware,
        "data": False,
    }

    if payload is not None:
        result.update({"data": True})
        sinfo += ', Object data: ' + payload.hex()
        # loop through parse_xiaomi payload
        payload_start = 0
        payload_length = len(payload)
        # assume that the data may have several values of different types
        while payload_length >= payload_start + 3:
            obj_typecode = payload[payload_start] + (payload[payload_start + 1] << 8)
            obj_length = payload[payload_start + 2]
            next_start = payload_start + 3 + obj_length
            if payload_length < next_start:
                _LOGGER.debug("Invalid payload data length, payload: %s", payload.hex())
                break
            dobject = payload[payload_start + 3:next_start]
            if obj_length != 0:
                resfunc = xiaomi_dataobject_dict.get(obj_typecode, None)
                if resfunc:
                    if hex(obj_typecode) in ["0x1001", "0xf"]:
                        result.update(resfunc(dobject, device_type))
                    else:
                        result.update(resfunc(dobject))
                else:
                    if self.report_unknown == "Xiaomi":
                        _LOGGER.info("%s, UNKNOWN dataobject in payload! Adv: %s", sinfo, data.hex())
            payload_start = next_start

    return result


def decrypt_mibeacon_v4_v5(self, data, i, xiaomi_mac):
    # check for minimum length of encrypted advertisement
    if len(data) < i + 9:
        _LOGGER.debug("Invalid data length (for decryption), adv: %s", data.hex())
    # try to find encryption key for current device
    try:
        key = self.aeskeys[xiaomi_mac]
        if len(key) != 16:
            _LOGGER.error("Encryption key should be 16 bytes (32 characters) long")
            return None
    except KeyError:
        # no encryption key found
        _LOGGER.error("No encryption key found for device with MAC %s", to_mac(xiaomi_mac))
        return None

    nonce = b"".join([xiaomi_mac[::-1], data[6:9], data[-7:-4]])
    aad = b"\x11"
    token = data[-4:]
    cipherpayload = data[i:-7]
    cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
    cipher.update(aad)

    try:
        decrypted_payload = cipher.decrypt_and_verify(cipherpayload, token)
    except ValueError as error:
        _LOGGER.warning("Decryption failed: %s", error)
        _LOGGER.debug("token: %s", token.hex())
        _LOGGER.debug("nonce: %s", nonce.hex())
        _LOGGER.debug("cipherpayload: %s", cipherpayload.hex())
        return None
    if decrypted_payload is None:
        _LOGGER.error(
            "Decryption failed for %s, decrypted payload is None",
            to_mac(xiaomi_mac),
        )
        return None
    return decrypted_payload


def decrypt_mibeacon_legacy(self, data, i, xiaomi_mac):
    # check for minimum length of encrypted advertisement
    if len(data) < i + 7:
        _LOGGER.debug("Invalid data length (for decryption), adv: %s", data.hex())
    # try to find encryption key for current device
    try:
        aeskey = self.aeskeys[xiaomi_mac]
        if len(aeskey) != 12:
            _LOGGER.error("Encryption key should be 12 bytes (24 characters) long")
            return None
        key = b"".join([aeskey[0:6], bytes.fromhex("8d3d3c97"), aeskey[6:]])
    except KeyError:
        # no encryption key found
        _LOGGER.error("No encryption key found for device with MAC %s", to_mac(xiaomi_mac))
        return None

    nonce = b"".join([data[4:9], data[-4:-1], xiaomi_mac[::-1][:-1]])
    aad = b"\x11"
    cipherpayload = data[i:-4]
    cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
    cipher.update(aad)

    try:
        decrypted_payload = cipher.decrypt(cipherpayload)
    except ValueError as error:
        _LOGGER.warning("Decryption failed: %s", error)
        _LOGGER.debug("nonce: %s", nonce.hex())
        _LOGGER.debug("cipherpayload: %s", cipherpayload.hex())
        return None
    if decrypted_payload is None:
        _LOGGER.warning(
            "Decryption failed for %s, decrypted payload is None",
            to_mac(xiaomi_mac),
        )
        return None
    return decrypted_payload


def to_mac(addr: int):
    """Return formatted MAC address"""
    return ':'.join(f'{i:02X}' for i in addr)
