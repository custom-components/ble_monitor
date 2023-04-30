"""Parser for BluStream BLE advertisements."""
import logging
from struct import unpack

from .helpers import (
    to_mac,
    to_unformatted_mac,
)

_LOGGER = logging.getLogger(__name__)


def parse_blustream(self, data, source_mac, rssi):
    """Parse BluStream advertisement."""
    msg_length = len(data)
    firmware = "BluStream"
    blustream_mac = source_mac
    msg = data[8:]

    if msg_length == 13:
        # BluStream
        device_type = "BluStream"
        (acc, humi, temp) = unpack(">BHh", msg)
        result = {
            "temperature": temp / 100,
            "humidity": humi / 100,
            "acceleration": acc,
            "acceleration x": 0,
            "acceleration y": 0,
            "acceleration z": 0
        }
    else:
        if self.report_unknown == "BluStream":
            _LOGGER.info(
                "BLE ADV from UNKNOWN BluStream DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in whitelist, if needed
    if self.discovery is False and blustream_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(blustream_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": to_unformatted_mac(blustream_mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result
