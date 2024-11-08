"""Parser for Blustream BLE advertisements."""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_blustream(self, data: bytes, mac: bytes):
    """Parse Blustream advertisement."""
    msg_length = len(data)
    firmware = "Blustream"
    blustream_mac = mac
    msg = data[8:]

    if msg_length == 13:
        # Blustream
        device_type = "Blustream"
        (acc, humi, temp) = unpack(">BHh", msg)
        result = {
            "temperature": temp / 100,
            "humidity": humi / 100,
            "acceleration": acc,
        }
    else:
        if self.report_unknown == "Blustream":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Blustream DEVICE: MAC: %s, ADV: %s",
                to_mac(mac),
                data.hex()
            )
        return None

    result.update({
        "mac": to_unformatted_mac(blustream_mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result
