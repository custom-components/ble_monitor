"""Parser for Thermobeacon BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_thermobeacon(self, data: bytes, mac: bytes):
    """Thermobeacon parser"""
    msg_length = len(data)
    device_id = data[2]
    firmware = "Thermobeacon"

    if msg_length == 21 and device_id == 0x55:
        device_type = "T201"
        thermobeacon_mac = data[6:12]

        xvalue = data[12:19]
        (volt, temp, humi, batt) = unpack(">HhHB", xvalue)
        result = {
            "temperature": temp / 100,
            "humidity": humi / 100,
            "voltage": volt / 100,
            "battery": batt
        }
    elif msg_length == 22:
        if device_id == 0x10:
            device_type = "Lanyard/mini hygrometer"
        elif device_id in [0x11, 0x15, 0x18, 0x1B]:
            device_type = "Smart hygrometer"
        else:
            device_type = None

        thermobeacon_mac_reversed = data[6:12]
        thermobeacon_mac = thermobeacon_mac_reversed[::-1]

        xvalue = data[12:18]
        (volt, temp, humi) = unpack("<HhH", xvalue)

        if volt >= 3000:
            batt = 100
        elif volt >= 2600:
            batt = 60 + (volt - 2600) * 0.1
        elif volt >= 2500:
            batt = 40 + (volt - 2500) * 0.2
        elif volt >= 2450:
            batt = 20 + (volt - 2450) * 0.4
        else:
            batt = 0
        result = {
            "voltage": volt / 1000,
            "temperature": temp / 16,
            "humidity": humi / 16,
            "battery": batt
        }
    else:
        device_type = None

    if device_type is None:
        if self.report_unknown == "Thermobeacon":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Thermobeacon DEVICE: MAC: %s, ADV: %s",
                to_mac(mac),
                data.hex()
            )
        return None

    # check for MAC presence in message and in service data
    if thermobeacon_mac != mac:
        _LOGGER.debug("Invalid MAC address for Thermobeacon device")
        return None

    result.update({
        "mac": to_unformatted_mac(mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result
