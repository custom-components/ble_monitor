"""Parser for Xiaomi MiBeacon BLE advertisements"""
import logging
import math
import struct

from Cryptodome.Cipher import AES
from homeassistant.util import datetime

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)

# Device type dictionary
# {device type code: device name}
XIAOMI_TYPE_DICT = {
    0x0C3C: "CGC1",
    0x0576: "CGD1",
    0x066F: "CGDK2",
    0x0347: "CGG1",
    0x0B48: "CGG1-ENCRYPTED",
    0x03D6: "CGH1",
    0x0A83: "CGPR1",
    0x03BC: "GCLS002",
    0x0098: "HHCCJCY01",
    0x015D: "HHCCPOT002",
    0x02DF: "JQJCY01YM",
    0x0997: "JTYJGD03MI",
    0x1568: "K9B-1BTN",
    0x1569: "K9B-2BTN",
    0x0DFD: "K9B-3BTN",
    0x1C10: "K9BB-1BTN",
    0x1889: "MS1BB(MI)",
    0x2AEB: "HS1BB(MI)",
    0x01AA: "LYWSDCGQ",
    0x045B: "LYWSD02",
    0x16e4: "LYWSD02MMC",
    0x2542: "LYWSD02MMC",
    0x055B: "LYWSD03MMC",
    0x098B: "MCCGQ02HL",
    0x06d3: "MHO-C303",
    0x0387: "MHO-C401",
    0x07F6: "MJYD02YL",
    0x04E9: "MJZNMSQ01YD",
    0x2832: "MJWSD05MMC",
    0x00DB: "MMC-T201-1",
    0x0391: "MMC-W505",
    0x03DD: "MUE4094RT",
    0x0489: "M1S-T500",
    0x0806: "T700",
    0x1790: "T700i",
    0x0A8D: "RTCGQ02LM",
    0x0863: "SJWS01LM",
    0x045C: "V-SK152",
    0x040A: "WX08ZM",
    0x04E1: "XMMF01JQD",
    0x1203: "XMWSDJ04MMC",
    0x1949: "XMWXKG01YL",
    0x2387: "XMWXKG01LM",
    0x098C: "XMZNMST02YD",
    0x0784: "XMZNMS04LM",
    0x0E39: "XMZNMS08LM",
    0x07BF: "YLAI003",
    0x0153: "YLYK01YL",
    0x068E: "YLYK01YL-FANCL",
    0x04E6: "YLYK01YL-VENFAN",
    0x03BF: "YLYB01YL-BHFRC",
    0x03B6: "YLKG07YL/YLKG08YL",
    0x0083: "YM-K1501",
    0x0113: "YM-K1501EU",
    0x069E: "ZNMS16LM",
    0x069F: "ZNMS17LM",
    0x0380: "DSL-C08",
    0x0DE7: "SU001-T",
    0x20DB: "MJZNZ018H",
    0x55B5: "MJWSD06MMC",
    0x18E3: "ZX1",
    0x11C2: "SV40",
    0x3F0F: "RS1BB",
    0x38BB: "PTX",
    0x3531: "XMPIRO2SXS",
    0x3F4C: "PS1BB",
    0x3A61: "KS1",
    0x3E17: "KS1BP",
    0x50FB: "ES3",
    0x5DB1: "MBS17"
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
    0b0000: [1, "lock", "unlock outside the door"],
    0b0001: [0, "lock", "lock"],
    0b0010: [0, "antilock", "turn on anti-lock"],
    0b0011: [1, "antilock", "turn off anti-lock"],
    0b0100: [1, "lock", "unlock inside the door"],
    0b0101: [0, "lock", "lock inside the door"],
    0b0110: [0, "childlock", "turn on child lock"],
    0b0111: [1, "childlock", "turn off child lock"],
    0b1000: [0, "lock", "lock outside the door"],
    0b1111: [1, "lock", "abnormal"],
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
# https://iot.mi.com/new/doc/accesses/direct-access/embedded-development/ble/object-definition
def obj0003(xobj):
    """Motion"""
    return {"motion": xobj[0], "motion timer": xobj[0]}


def obj0006(xobj):
    """Fingerprint"""
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


def obj0007(xobj):
    """Door"""
    door_byte = xobj[0]
    if door_byte == 0x00:
        action = "open the door"
        door = 1
    elif door_byte == 0x01:
        action = "close the door"
        door = 0
    elif door_byte == 0x02:
        action = "timeout, not closed"
        door = 1
    elif door_byte == 0x03:
        action = "knock on the door"
        door = 0
    elif door_byte == 0x04:
        action = "pry the door"
        door = 1
    elif door_byte == 0x05:
        action = "door stuck"
        door = 0
    else:
        return {}
    return {"door": door, "door action": action}


def obj0008(xobj, device_type):
    """armed away"""
    return_data = {}
    value = xobj[0] ^ 1
    return_data.update({'armed away': value})
    if len(xobj) == 5:
        timestamp = int.from_bytes(xobj[1:], 'little')
        timestamp = datetime.fromtimestamp(timestamp).isoformat()
        return_data.update({'timestamp': timestamp})
    # Lift up door handle outside the door sends this event from DSL-C08.
    if device_type == "DSL-C08":
        return {
            "lock": value,
            "locktype": 'lock',
            "action": 'lock outside the door',
            "method": "manual",
            "error": None,
            "key id": None,
            "timestamp": None,
        }
    return return_data


def obj0010(xobj):
    """Toothbrush"""
    if xobj[0] == 0:
        if len(xobj) == 1:
            return {'toothbrush': 1}
        else:
            return {'toothbrush': 1, 'counter': xobj[1]}
    else:
        if len(xobj) == 1:
            return {'toothbrush': 0}
        else:
            return {'toothbrush': 0, 'score': xobj[1]}


def obj000a(xobj):
    """Body temperature"""
    if len(xobj) == 2:
        (temp,) = T_STRUCT.unpack(xobj)
        if temp:
            return {"temperature": temp / 100}
        else:
            return {}
    else:
        return {}


def obj000b(xobj, device_type):
    """Lock"""
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
        # Decouple lock by type on some devices
        lock_type = "lock"
        if device_type == "ZNMS17LM":
            lock_type = BLE_LOCK_ACTION[action][1]
        action = BLE_LOCK_ACTION[action][2]
        method = BLE_LOCK_METHOD[method]

        # Biometric unlock then disarm
        if device_type == "DSL-C08":
            if method == "password":
                if 5000 <= key_id < 6000:
                    method = "one-time password"

        return {
            lock_type: lock,
            "locktype": lock_type,
            "action": action,
            "method": method,
            "error": error,
            "key id": key_id,
            "timestamp": timestamp,
        }
    else:
        return {}


def obj000f(xobj, device_type):
    """Moving with light"""
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
    """button"""
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

        # press type and dimmer steps
        button_press_type = "no press"
        btn_switch_press_type = "no press"
        steps = None

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
                steps = value
            if button_type == 1:
                button_press_type = "long press"
                steps = value
        elif press == 4:
            if button_type == 0:
                if value <= 127:
                    button_press_type = "rotate right"
                    steps = value
                else:
                    button_press_type = "rotate left"
                    steps = 256 - value
            elif button_type <= 127:
                button_press_type = "rotate right (pressed)"
                steps = button_type
            else:
                button_press_type = "rotate left (pressed)"
                steps = 256 - button_type
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
            result["steps"] = steps
            result["dimmer"] = button_press_type
        elif device_type == "K9B-1BTN":
            result["button switch"] = btn_switch_press_type
            result["one btn switch"] = one_btn_switch
        elif device_type == "K9B-2BTN":
            result["button switch"] = btn_switch_press_type
            if two_btn_switch_left:
                result["two btn switch left"] = two_btn_switch_left
            if two_btn_switch_right:
                result["two btn switch right"] = two_btn_switch_right
        elif device_type == "K9B-3BTN":
            result["button switch"] = btn_switch_press_type
            if three_btn_switch_left:
                result["three btn switch left"] = three_btn_switch_left
            if three_btn_switch_middle:
                result["three btn switch middle"] = three_btn_switch_middle
            if three_btn_switch_right:
                result["three btn switch right"] = three_btn_switch_right
        else:
            return None
        return result

    else:
        return None


def obj1004(xobj):
    """Temperature"""
    if len(xobj) == 2:
        (temp,) = T_STRUCT.unpack(xobj)
        return {"temperature": temp / 10}
    else:
        return {}


def obj1005(xobj):
    """Switch and Temperature"""
    return {"switch": xobj[0], "temperature": xobj[1]}


def obj1006(xobj):
    """Humidity"""
    if len(xobj) == 2:
        (humi,) = H_STRUCT.unpack(xobj)
        return {"humidity": humi / 10}
    else:
        return {}


def obj1007(xobj):
    """Illuminance"""
    if len(xobj) == 3:
        (illum,) = ILL_STRUCT.unpack(xobj + b'\x00')
        return {"illuminance": illum, "light": 1 if illum == 100 else 0}
    else:
        return {}


def obj1008(xobj):
    """Moisture"""
    return {"moisture": xobj[0]}


def obj1009(xobj):
    """Conductivity"""
    if len(xobj) == 2:
        (cond,) = CND_STRUCT.unpack(xobj)
        return {"conductivity": cond}
    else:
        return {}


def obj1010(xobj):
    """Formaldehyde"""
    if len(xobj) == 2:
        (fmdh,) = FMDH_STRUCT.unpack(xobj)
        return {"formaldehyde": fmdh / 100}
    else:
        return {}


def obj1012(xobj):
    """Switch"""
    return {"switch": xobj[0]}


def obj1013(xobj):
    """Consumable (in percent)"""
    return {"consumable": xobj[0]}


def obj1014(xobj):
    """Moisture detected (wet/dry)"""
    return {"moisture detected": xobj[0]}


def obj1015(xobj):
    """Smoke"""
    return {"smoke": xobj[0]}


def obj1017(xobj):
    """No motion"""
    if len(xobj) == 4:
        (no_motion_time,) = M_STRUCT.unpack(xobj)
        # seconds since last motion detected message (not used, we use motion timer in obj000f)
        # 0 = motion detected
        return {"motion": 1 if no_motion_time == 0 else 0, "no motion time": no_motion_time}
    else:
        return {}


def obj1018(xobj):
    """Light intensity"""
    return {"light": xobj[0]}


def obj1019(xobj):
    """Door/Window sensor"""
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


def obj101b(xobj):
    """Timeout no movement"""
    if len(xobj) == 4:
        (no_motion_time,) = M_STRUCT.unpack(xobj)
        # seconds since last motion detected message (not used, we use motion timer in obj000f)
        # 0 = motion detected
        return {"motion": 1 if no_motion_time == 0 else 0, "no motion time": no_motion_time}
    else:
        return {}


def obj100a(xobj):
    """Battery"""
    batt = xobj[0]
    volt = 2.2 + (3.1 - 2.2) * (batt / 100)
    return {"battery": batt, "voltage": volt}


def obj100d(xobj):
    """Temperature and humidity"""
    if len(xobj) == 4:
        (temp, humi) = TH_STRUCT.unpack(xobj)
        return {"temperature": temp / 10, "humidity": humi / 10}
    else:
        return {}


def obj100e(xobj, device_type):
    """Lock common attribute"""
    # https://iot.mi.com/new/doc/accesses/direct-access/embedded-development/ble/object-definition#%E9%94%81%E5%B1%9E%E6%80%A7
    if len(xobj) == 1:
        # Unlock by type on some devices
        if device_type == "DSL-C08":
            lock_attribute = int.from_bytes(xobj, 'little')
            lock = lock_attribute & 0x01 ^ 1
            childlock = lock_attribute >> 3 ^ 1
            return {"childlock": childlock, "lock": lock}


def obj2000(xobj):
    """Body temperature"""
    if len(xobj) == 5:
        (temp1, temp2, bat) = TTB_STRUCT.unpack(xobj)
        # Body temperature is calculated from the two measured temperatures.
        # Formula is based on approximation based on values in the app in the range 36.5 - 37.8.
        body_temp = (
            3.71934 * pow(10, -11) * math.exp(0.69314 * temp1 / 100) - (
                1.02801 * pow(10, -8) * math.exp(0.53871 * temp2 / 100)
            ) + 36.413
        )
        return {"temperature": body_temp, "battery": bat}
    else:
        return {}


def obj3003(xobj):
    """Brushing"""
    result = {}
    print("brush %s", xobj.hex())
    start_obj = xobj[0]
    if start_obj == 0:
        # Start of brushing
        result["toothbrush"] = 1
        start_time = struct.unpack('<L', xobj[1:5])[0]
        result["start time"] = datetime.fromtimestamp(start_time)
    elif start_obj == 1:
        # End of brushing
        result["toothbrush"] = 0
        end_time = struct.unpack('<L', xobj[1:5])[0]
        result["end time"] = datetime.fromtimestamp(end_time)

    if len(xobj) == 6:
        result["score"] = xobj[5]
    return result


# The following data objects are device specific. For now only added for
# LYWSD02MMC, XMWSDJ04MMC, MJWSD05MMC, XMWXKG01YL, LINPTECH MS1BB(MI), HS1BB(MI), K9BB
# https://miot-spec.org/miot-spec-v2/instances?status=all

def obj4801(xobj):
    """Temperature"""
    (temp,) = struct.unpack("f", xobj)
    return {"temperature": temp}


def obj4802(xobj):
    """Humidity"""
    if len(xobj) == 1:
        humi = xobj[0]
        return {"humidity": humi}
    else:
        return {}


def obj4803(xobj):
    """Battery"""
    batt = xobj[0]
    return {"battery": batt}


def obj4804(xobj):
    """Opening status"""
    opening_state = xobj[0]
    # Status of the door/window, used in combination with obj4a12
    if opening_state == 1:
        opening = 1
    elif opening_state == 2:
        opening = 0
    else:
        return {}
    return {"opening": opening}


def obj4805(xobj):
    """Illuminance in lux"""
    (illu,) = struct.unpack("f", xobj)
    return {"illuminance": illu}


def obj4806(xobj):
    """Moisture detected (wet/dry)"""
    wet = xobj[0]
    return {"moisture detected": wet}


def obj4808(xobj):
    """Humidity"""
    (humi,) = struct.unpack("f", xobj)
    return {"humidity": humi}


def obj4810(xobj):
    """Sleep State"""
    sleep_state = xobj[0]
    if sleep_state == 0:
        return {"sleeping": 0}
    elif sleep_state == 1:
        return {"sleeping": 1}
    elif sleep_state == 2:
        return {"button switch": "double press"}
    else:
        return None


def obj4811(xobj):
    """Snoring State"""
    return {"snoring": xobj[0]}


def obj4818(xobj):
    """Time in seconds of no motion (not used, we use 4a08)"""
    if len(xobj) == 2:
        (no_motion_time,) = struct.unpack("<H", xobj)
        # seconds since last motion detected message (not used, we use motion timer in obj4a08)
        # 0 = motion detected
        return {"motion": 1 if no_motion_time == 0 else 0, "no motion time": no_motion_time}
    else:
        return {}


def obj483c(xobj):
    """Pressure Present State"""
    return {"pressure state": xobj[0]}


def obj483d(xobj):
    """Pressure Present Duration"""
    (duration,) = struct.unpack("<I", xobj)
    return {"pressure present duration": duration}


def obj483e(xobj):
    """Pressure Not Present Duration"""
    (duration,) = struct.unpack("<I", xobj)
    return {"pressure not present duration": duration}


def obj483f(xobj):
    """Pressure present time set"""
    (duration,) = struct.unpack("<I", xobj)
    return {"pressure present time set": duration}


def obj4840(xobj):
    """Pressure Not Present Time Set"""
    (duration,) = struct.unpack("<I", xobj)
    return {"pressure not present time set": duration}


def obj484e(xobj):
    """Occupancy Status"""
    (occupancy,) = struct.unpack("<B", xobj)
    if occupancy == 0:
        # no motion is being taken care of by the timer in HA
        return {}
    else:
        return {"motion": 1, "motion timer": 1}


def obj484f(xobj):
    """Time in minutes of no motion (not used, we use 484e)"""
    if len(xobj) == 1:
        (no_motion_time,) = struct.unpack("<B", xobj)
        # minutes of no motion (not used, we use motion timer in obj4a08)
        # 0 = motion detected
        return {"motion": 1 if no_motion_time == 0 else 0, "no motion time": no_motion_time}
    else:
        return {}


def obj4850(xobj):
    """Time in minutes with motion (not used, we use 484e)"""
    (motion_time,) = struct.unpack("<B", xobj)
    # minutes with motion (not used, we use motion timer in obj484e)
    return {"motion time": motion_time}


def obj4a01(xobj):
    """Low Battery"""
    low_batt = xobj[0]
    return {"low battery": low_batt}


def obj4a08(xobj):
    """Motion detected with Illuminance in lux"""
    (illu,) = struct.unpack("f", xobj)
    return {"motion": 1, "motion timer": 1, "illuminance": illu}


def obj4a0c(xobj):
    """Single click PTX"""
    return {
        "one btn switch": "toggle",
        "button switch": "single press",
    }


def obj4a0d(xobj):
    """Double click PTX"""
    return {
        "one btn switch": "toggle",
        "button switch": "double press",
    }


def obj4a0e(xobj):
    """Long click PTX"""
    return {
        "one btn switch": "toggle",
        "button switch": "long press",
    }


def obj4a0f(xobj):
    """Door/window broken open"""
    dev_forced = xobj[0]
    if dev_forced == 1:
        return {
            "opening": 1,
            "status": "door/window broken open"
        }
    else:
        return {}


def obj4a12(xobj):
    """Opening event"""
    opening_state = xobj[0]
    # Opening event, used in combination with obj4804
    if opening_state == 1:
        opening = 1
    elif opening_state == 2:
        opening = 0
    else:
        return {}
    return {"opening": opening}


def obj4a13(xobj):
    """Button"""
    click = xobj[0]
    if click == 1:
        return {"button": "toggle"}
    else:
        return {}


def obj4a1a(xobj):
    """Door Not Closed"""
    if xobj[0] == 1:
        return {
            "opening": 1,
            "status": "door not closed"}
    else:
        return {}


def obj4a1c(xobj):
    """Device reset"""
    reset = xobj[0]
    return {"reset": reset}


def obj4c01(xobj):
    """Temperature"""
    if len(xobj) == 4:
        temp = FLOAT_STRUCT.unpack(xobj)[0]
        return {"temperature": temp}
    else:
        return {}


def obj4c02(xobj):
    """Humidity"""
    if len(xobj) == 1:
        humi = xobj[0]
        return {"humidity": humi}
    else:
        return {}


def obj4c03(xobj):
    """Battery"""
    batt = xobj[0]
    return {"battery": batt}


def obj4c08(xobj):
    """Humidity"""
    if len(xobj) == 4:
        humi = FLOAT_STRUCT.unpack(xobj)[0]
        return {"humidity": humi}
    else:
        return {}


def obj4c14(xobj):
    """Mode"""
    mode = xobj[0]
    return {"mode": mode}


def obj4e01(xobj):
    """Low Battery"""
    low_batt = xobj[0]
    return {"low battery": low_batt}


def obj4e0c(xobj, device_type):
    """Click"""
    if device_type == "XMWXKG01YL":
        click = xobj[0]
        if click == 1:
            result = {
                "two btn switch left": "toggle",
                "button switch": "single press",
            }
        elif click == 2:
            result = {
                "two btn switch right": "toggle",
                "button switch": "single press",
            }
        elif click == 3:
            result = {
                "two btn switch left": "toggle",
                "two btn switch right": "toggle",
                "button switch": "single press",
            }
    elif device_type == "K9BB-1BTN":
        click = xobj[0]
        if click == 1:
            result = {
                "one btn switch": "toggle",
                "button switch": "single press",
            }
        elif click == 8:
            result = {
                "one btn switch": "toggle",
                "button switch": "long press",
            }
        elif click == 15:
            result = {
                "one btn switch": "toggle",
                "button switch": "double press",
            }
    elif device_type == "XMWXKG01LM":
        result = {
            "one btn switch": "toggle",
            "button switch": "single press",
        }
    else:
        result = {}
    return result


def obj4e0d(xobj, device_type):
    """Double Click"""
    if device_type == "XMWXKG01YL":
        click = xobj[0]
        if click == 1:
            result = {
                "two btn switch left": "toggle",
                "button switch": "double press",
            }
        elif click == 2:
            result = {
                "two btn switch right": "toggle",
                "button switch": "double press",
            }
        elif click == 3:
            result = {
                "two btn switch left": "toggle",
                "two btn switch right": "toggle",
                "button switch": "double press",
            }
    elif device_type == "XMWXKG01LM":
        result = {
            "one btn switch": "toggle",
            "button switch": "double press",
        }
    else:
        result = {}
    return result


def obj4e0e(xobj, device_type):
    """Long Press"""
    if device_type == "XMWXKG01YL":
        click = xobj[0]
        if click == 1:
            result = {
                "two btn switch left": "toggle",
                "button switch": "long press",
            }
        elif click == 2:
            result = {
                "two btn switch right": "toggle",
                "button switch": "long press",
            }
        elif click == 3:
            result = {
                "two btn switch left": "toggle",
                "two btn switch right": "toggle",
                "button switch": "long press",
            }
    elif device_type == "XMWXKG01LM":
        result = {
            "one btn switch": "toggle",
            "button switch": "long press",
        }
    else:
        result = {}
    return result


def obj4e16(xobj):
    """Bed occupancy"""
    event = xobj[0]
    if event == 1:
        return {"bed occupancy": 1}
    else:
        return None


def obj4e17(xobj):
    """Bed occupancy"""
    event = xobj[0]
    if event == 1:
        return {"bed occupancy": 0}
    else:
        return None


def obj4e1c(xobj):
    """Device reset"""
    return {"device reset": xobj[0]}


def obj5003(xobj):
    """Battery"""
    batt = xobj[0]
    return {"battery": batt}


def obj5010(xobj):
    """Sleep State"""
    sleep_state = xobj[0]
    if sleep_state == 0:
        return {"sleeping": 0}
    elif sleep_state == 1:
        return {"sleeping": 1}
    elif sleep_state == 2:
        return {"button": "double press"}
    else:
        return None


def obj5011(xobj):
    """Snoring State"""
    return {"snoring": xobj[0]}


def obj5403(xobj):
    """Battery level"""
    return {"battery": xobj[0]}


def obj5414(xobj):
    """Mode"""
    mode = xobj[0]
    return {"mode": mode}


def obj5601(xobj):
    """Low Battery"""
    low_batt = xobj[0]
    return {"low battery": low_batt}


def obj560c(xobj, device_type):
    """Click"""
    if device_type in ["KS1", "KS1BP"]:
        click = xobj[0]
        if click == 1:
            result = {
                "four btn switch 1": "toggle",
                "button switch": "single press",
            }
        elif click == 2:
            result = {
                "four btn switch 2": "toggle",
                "button switch": "single press",
            }
        elif click == 3:
            result = {
                "four btn switch 3": "toggle",
                "button switch": "single press",
            }
        elif click == 4:
            result = {
                "four btn switch 4": "toggle",
                "button switch": "single press",
            }
        else:
            result = None
        return result
    else:
        return None


def obj560d(xobj, device_type):
    """Click"""
    if device_type in ["KS1", "KS1BP"]:
        click = xobj[0]
        if click == 1:
            result = {
                "four btn switch 1": "toggle",
                "button switch": "double press",
            }
        elif click == 2:
            result = {
                "four btn switch 2": "toggle",
                "button switch": "double press",
            }
        elif click == 3:
            result = {
                "four btn switch 3": "toggle",
                "button switch": "double press",
            }
        elif click == 4:
            result = {
                "four btn switch 4": "toggle",
                "button switch": "double press",
            }
        else:
            result = None
        return result
    else:
        return None


def obj560e(xobj, device_type):
    """Click"""
    if device_type in ["KS1", "KS1BP"]:
        click = xobj[0]
        if click == 1:
            result = {
                "four btn switch 1": "toggle",
                "button switch": "long press",
            }
        elif click == 2:
            result = {
                "four btn switch 2": "toggle",
                "button switch": "long press",
            }
        elif click == 3:
            result = {
                "four btn switch 3": "toggle",
                "button switch": "long press",
            }
        elif click == 4:
            result = {
                "four btn switch 4": "toggle",
                "button switch": "long press",
            }
        else:
            result = None
        return result
    else:
        return None


def obj5a16(xobj):
    """Bed occupancy"""
    event = xobj[0]
    if event == 1:
        return {"bed occupancy": 1}
    elif event == 2:
        return {"bed occupancy": 0}
    elif event == 3:
        return {"button": "double press"}
    else:
        return None


# Dataobject dictionary
# {dataObject_id: (converter}
xiaomi_dataobject_dict = {
    0x0003: obj0003,
    0x0006: obj0006,
    0x0007: obj0007,
    0x0008: obj0008,
    0x0010: obj0010,
    0x000A: obj000a,
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
    0x101B: obj101b,
    0x100A: obj100a,
    0x100D: obj100d,
    0x100E: obj100e,
    0x2000: obj2000,
    0x3003: obj3003,
    0x4801: obj4801,
    0x4802: obj4802,
    0x4803: obj4803,
    0x4804: obj4804,
    0x4805: obj4805,
    0x4806: obj4806,
    0x4808: obj4808,
    0x4810: obj4810,
    0x4811: obj4811,
    0x4818: obj4818,
    0x483c: obj483c,
    0x483d: obj483d,
    0x483e: obj483e,
    0x483f: obj483f,
    0x4840: obj4840,
    0x484e: obj484e,
    0x484f: obj484f,
    0x4850: obj4850,
    0x4a01: obj4a01,
    0x4a08: obj4a08,
    0x4a0c: obj4a0c,
    0x4a0d: obj4a0d,
    0x4a0e: obj4a0e,
    0x4a0f: obj4a0f,
    0x4a12: obj4a12,
    0x4a13: obj4a13,
    0x4a1a: obj4a1a,
    0x4a1c: obj4a1c,
    0x4c01: obj4c01,
    0x4c02: obj4c02,
    0x4c03: obj4c03,
    0x4c08: obj4c08,
    0x4c14: obj4c14,
    0x4e01: obj4e01,
    0x4e0c: obj4e0c,
    0x4e0d: obj4e0d,
    0x4e0e: obj4e0e,
    0x4e16: obj4e16,
    0x4e17: obj4e17,
    0x4e1c: obj4e1c,
    0x5003: obj5003,
    0x5010: obj5010,
    0x5011: obj5011,
    0x5403: obj5403,
    0x5414: obj5414,
    0x5601: obj5601,
    0x560c: obj560c,
    0x560d: obj560d,
    0x560e: obj560e,
    0x5a16: obj5a16,
}


def parse_xiaomi(self, data: bytes, mac: bytes):
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
        if xiaomi_mac != mac:
            _LOGGER.debug("Xiaomi MAC address doesn't match data MAC address. Data: %s", data.hex())
            return None

    # determine the device type
    device_id = data[6] + (data[7] << 8)
    try:
        device_type = XIAOMI_TYPE_DICT[device_id]
    except KeyError:
        if self.report_unknown == "Xiaomi":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Xiaomi device: MAC: %s, ADV: %s",
                to_mac(mac),
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

    # check for unique packet_id and advertisement priority
    try:
        prev_packet = self.lpacket_ids[mac]
    except KeyError:
        # start with empty first packet
        prev_packet = None

    if device_type in ["LYWSD03MMC", "CGG1", "MHO-C401", "CGDK2"]:
        # Check for adv priority and packet_id for devices that can also send in ATC format
        adv_priority = 19
        try:
            prev_adv_priority = self.adv_priority[mac]
        except KeyError:
            # start with initial adv priority
            prev_adv_priority = 0
        if adv_priority > prev_adv_priority:
            # always process advertisements with a higher priority
            self.adv_priority[mac] = adv_priority
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
            self.adv_priority[mac] = prev_adv_priority
            return None
    else:
        if prev_packet == packet_id:
            if self.filter_duplicates is True:
                # only process messages with highest priority and messages with unique packet id
                return None
    self.lpacket_ids[mac] = packet_id

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
                payload = decrypt_mibeacon_legacy(self, data, i, mac)
            else:
                payload = decrypt_mibeacon_v4_v5(self, data, i, mac)
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
        "mac": to_unformatted_mac(mac),
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
            if dobject and obj_length != 0 or hex(obj_typecode) in [
                "0x4a0c", "0x4a0d", "0x4a0e", "0x4e0c", "0x4e0d", "0x4e0e"
            ]:
                resfunc = xiaomi_dataobject_dict.get(obj_typecode, None)
                if resfunc:
                    if hex(obj_typecode) in [
                        "0x8",
                        "0x100e",
                        "0x1001",
                        "0xf",
                        "0xb",
                        "0x4e0c",
                        "0x4e0d",
                        "0x4e0e",
                        "0x560c",
                        "0x560d",
                        "0x560e"
                    ]:
                        result.update(resfunc(dobject, device_type))
                    else:
                        result.update(resfunc(dobject))
                else:
                    if self.report_unknown == "Xiaomi":
                        _LOGGER.info("%s, UNKNOWN dataobject in payload! Adv: %s", sinfo, data.hex())
            payload_start = next_start

    return result


def decrypt_mibeacon_v4_v5(self, data, i, mac):
    """decrypt MiBeacon v4/v5 encrypted advertisements"""
    # check for minimum length of encrypted advertisement
    if len(data) < i + 9:
        _LOGGER.debug("Invalid data length (for decryption), adv: %s", data.hex())
    # try to find encryption key for current device
    try:
        key = self.aeskeys[mac]
        if len(key) != 16:
            _LOGGER.error("Encryption key should be 16 bytes (32 characters) long")
            return None
    except KeyError:
        # no encryption key found
        if mac not in self.no_key_message:
            _LOGGER.error("No encryption key found for device with MAC %s", to_mac(mac))
            self.no_key_message.append(mac)
        return None

    nonce = b"".join([mac[::-1], data[6:9], data[-7:-4]])
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
            to_mac(mac),
        )
        return None
    return decrypted_payload


def decrypt_mibeacon_legacy(self, data, i, mac):
    """decrypt MiBeacon v2/v3 encrypted advertisements"""
    # check for minimum length of encrypted advertisement
    if len(data) < i + 7:
        _LOGGER.debug("Invalid data length (for decryption), adv: %s", data.hex())
    # try to find encryption key for current device
    try:
        aeskey = self.aeskeys[mac]
        if len(aeskey) != 12:
            _LOGGER.error("Encryption key should be 12 bytes (24 characters) long")
            return None
        key = b"".join([aeskey[0:6], bytes.fromhex("8d3d3c97"), aeskey[6:]])
    except KeyError:
        # no encryption key found
        _LOGGER.error("No encryption key found for device with MAC %s", to_mac(mac))
        return None

    nonce = b"".join([data[4:9], data[-4:-1], mac[::-1][:-1]])
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
            to_mac(mac),
        )
        return None
    return decrypted_payload
