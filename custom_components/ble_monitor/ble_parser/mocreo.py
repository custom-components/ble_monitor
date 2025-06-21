"""Parser for MOCREO BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)

MOCREO_TYPE_DICT = {
    0x81: "ST5",
    0x82: "SW2",
    0x83: "ST6",
    0x84: "ST8",
    0x86: "ST9",
    0x87: "ST10",
    0x8B: "MS1",
    0x8D: "MS2",
}

COMMON_DATA_PARSING_FORMAT = {
    "device_type": (1, 0, 8, False, None),
    "version": (3, 5, 4, False, None),
    "battery_percentage": (4, 1, 7, False, None),
    "connection_status": (5, 4, 1, False, None),
    "btn_state": (10, 6, 1, False, None),
}

MOCREO_TYPE_DATA_PARSING_FORMAT = {
    0x81: {
        "temperature": (6, 0, -16, True, lambda x: x / 100),
    },
    0x82: {
        "water leak": (10, 7, 1, False, None),
    },
    0x83: {
        "temperature": (6, 0, -16, True, lambda x: x / 100),
        "humidity": (8, 0, -16, True, lambda x: x / 100),
    },
    0x84: {
        "temperature": (6, 0, -16, True, lambda x: x / 100),
    },
    0x86: {
        "temperature": (6, 0, -16, True, lambda x: x / 100),
        "humidity": (8, 0, -16, True, lambda x: x / 100),
    },
    0x87: {
        "temperature": (6, 0, -16, True, lambda x: x / 100),
    },
    0x8B: {
        "temperature": (6, 0, -16, True, lambda x: x / 100),
    },
    0x8D: {
        "temperature": (6, 0, -16, True, lambda x: x / 100),
        "humidity": (8, 0, -16, True, lambda x: x / 100),
    },
}


def _get_value(source, pos):
    pos = list(pos)
    byteorder = "big" if pos[2] >= 0 else "little"
    pos[2] = abs(pos[2])

    if pos[2] >= (8 - pos[1]):
        end_bit_index = (pos[2] - (8 - pos[1])) % 8
        end_index = pos[0] + abs((pos[2] - (8 - pos[1])) // 8) + (1 if end_bit_index > 0 else 0)
    else:
        end_index = pos[0]
        end_bit_index = pos[2] + pos[1]

    shift_count = 8 - (8 if end_bit_index == 0 else end_bit_index)

    mask = 2 * (2 ** (pos[2] - 1) - 1) + 1
    mask = mask << shift_count

    res = mask & int.from_bytes(source[pos[0] : end_index + 1], byteorder)
    res = res >> shift_count

    if pos[3] and (res & 2 ** (pos[2] -1)) == 2 ** (pos[2] -1):
        res -= 2 ** (pos[2] - 1)
        res = -1 * ((res ^ (2 * (2 ** (pos[2] - 2) - 1) + 1)) + 1)

    if pos[4]:
        res = pos[4](res)

    return res

def parse_mocreo(self, data: bytes, local_name: str, mac: bytes):
    """Parser for MOCREO sensors"""
    common_data = data[2:]
    firmware = "MOCREO"
    result = {"firmware": firmware}

    device_type = _get_value(common_data, COMMON_DATA_PARSING_FORMAT["device_type"])
    version = _get_value(common_data, COMMON_DATA_PARSING_FORMAT["version"])
    battery = _get_value(common_data, COMMON_DATA_PARSING_FORMAT["battery_percentage"])

    if device_type in MOCREO_TYPE_DICT:
        device_name = MOCREO_TYPE_DICT[device_type]
        data_parsing_format = MOCREO_TYPE_DATA_PARSING_FORMAT[device_type]
        for key, value in data_parsing_format.items():
            result[key] = _get_value(common_data, value)
        result.update({
            "battery": battery,
            "data": True
        })
    else:
        _LOGGER.warning("Unknown device type: %s", device_type)
        return None

    result.update({
        "mac": to_unformatted_mac(mac),
        "type": device_name,
        "packet": "no packet id",
        "firmware": firmware,
    })
    return result
