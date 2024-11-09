"""Parser for Jaalee BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_jaalee(self, data: bytes, mac: bytes):
    """Jaalee parser"""
    msg_length = len(data)
    firmware = "Jaalee"
    result = {"firmware": firmware}
    if msg_length == 28 and data[1:4] == b'\xff\x4c\x00' and data[20:22] == b'\xf5\x25':
        device_type = "JHT"
        (temp, humi, _, batt) = unpack(">HHBB", data[22:])
        # data follows the iBeacon temperature and humidity definition
        temp = round(175 * temp / 65535 - 45, 2)
        humi = round(100 * humi / 65535, 2)

        result.update(
            {
                "temperature": temp,
                "humidity": humi,
                "battery": batt
            }
        )
    elif msg_length in [15, 16]:
        device_type = "JHT"
        batt = data[4]
        jaalee_mac_reversed = data[5:11]
        jaalee_mac = jaalee_mac_reversed[::-1]
        if jaalee_mac != mac:
            _LOGGER.debug(
                "Jaalee MAC address doesn't match data MAC address. "
                "Data: %s with source mac: %s and jaalee mac: %s",
                data.hex(),
                mac,
                jaalee_mac,
            )
            return None
        (temp, humi) = unpack(">HH", data[-4:])
        # data follows the iBeacon temperature and humidity definition
        temp = round(175 * temp / 65535 - 45, 2)
        humi = round(100 * humi / 65535, 2)

        result.update(
            {
                "temperature": temp,
                "humidity": humi,
                "battery": batt
            }
        )
    else:
        if self.report_unknown == "Jaalee":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Jaalee DEVICE: MAC: %s, ADV: %s",
                to_mac(mac),
                data.hex()
            )
        return None

    result.update({
        "mac": to_unformatted_mac(mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result
