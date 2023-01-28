# Parser for Xiaomi Mi Band BLE advertisements
import logging

from .helpers import (
    to_mac,
    to_unformatted_mac,
)

_LOGGER = logging.getLogger(__name__)


def parse_miband(self, data, source_mac, rssi):
    # check for data length
    msg_length = len(data)
    if msg_length == 28:
        device_type = "Mi Band"
        heart_rate = data[5]
        if heart_rate == 0xFF:
            return None
        result = {"heart rate": heart_rate}
    else:
        if self.report_unknown == "Mi Band":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Mi Band DEVICE: MAC: %s, ADV: %s",
                to_mac(source_mac),
                data.hex()
            )
        return None

    firmware = device_type

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and source_mac.lower() not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(source_mac))
        return None

    result.update({
        "type": device_type,
        "firmware": firmware,
        "mac": to_unformatted_mac(source_mac),
        "packet": 'no packet id',
        "rssi": rssi,
        "data": True,
    })
    return result
