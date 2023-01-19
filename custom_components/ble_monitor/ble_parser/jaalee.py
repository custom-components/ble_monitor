"""Parser for Jaalee BLE advertisements"""
import logging
from struct import unpack

from .helpers import (
    to_mac,
    to_unformatted_mac,
)

_LOGGER = logging.getLogger(__name__)


def parse_jaalee(self, data, source_mac, rssi):
    """Jaalee parser"""
    msg_length = len(data)
    firmware = "Jaalee"
    result = {"firmware": firmware}
    if msg_length == 28 and data[1:4] == b'\xff\x4c\x00' and data[20:22] == b'\xf5\x25':
        device_type = "JHT"
        jaalee_mac = source_mac
        (temp, humi, _, batt) = unpack(">HHBB", data[22:])
        # data follows the iBeacon temperature and humidity definition
        temp = round(175.72 * temp / 65536 - 46.85, 2)
        humi = round(125.0 * humi / 65536 - 6, 2)

        result.update(
            {
                "temperature": temp,
                "humidity": humi,
                "battery": batt
            }
        )
    elif msg_length == 15:
        device_type = "JHT"
        batt = data[4]
        jaalee_mac_reversed = data[5:11]
        jaalee_mac = jaalee_mac_reversed[::-1]
        if jaalee_mac != source_mac:
            _LOGGER.debug(
                "Jaalee MAC address doesn't match data MAC address. "
                "Data: %s with source mac: %s and jaalee mac: %s",
                data.hex(),
                source_mac,
                jaalee_mac,
            )
            return None
        (temp, humi) = unpack(">HH", data[11:])
        # data follows the iBeacon temperature and humidity definition
        temp = round(175.72 * temp / 65536 - 46.85, 2)
        humi = round(125.0 * humi / 65536 - 6, 2)

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
                "BLE ADV from UNKNOWN Jaalee DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and jaalee_mac.lower() not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(jaalee_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": to_unformatted_mac(jaalee_mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result
