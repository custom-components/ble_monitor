"""Parser for SmartDry BLE advertisements"""
import logging
from struct import unpack

from .helpers import (
    to_mac,
    to_unformatted_mac,
)

_LOGGER = logging.getLogger(__name__)


def parse_smartdry(self, data, source_mac, rssi):
    """Parser for SmartDry cloth dryer"""
    msg_length = len(data)
    smartdry_mac = source_mac
    if msg_length == 16:
        device_type = "SmartDry cloth dryer"
        firmware = "SmartDry"
        xvalue = data[4:16]
        (temp, humi, shake, batt, wake) = unpack("<IIHBB", xvalue)
        # The conversion isn't correct yet
        result = {
            "temperature": temp,
            "humidity": humi,
            "shake": shake,
            "battery": batt,
            "wake": wake
        }
    else:
        device_type = None
    if device_type is None:
        if self.report_unknown == "SmartDry":
            _LOGGER.info(
                "BLE ADV from UNKNOWN SmartDry DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and smartdry_mac.lower() not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(smartdry_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": to_unformatted_mac(smartdry_mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result
