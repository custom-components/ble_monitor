"""Parser for Thermopro BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_thermopro(self, data: bytes, device_type, mac: str):
    """Thermopro parser"""
    if device_type in ["TP357", "TP359"]:
        firmware = "Thermopro"
        xvalue = data[3:6]
        (temp, humi) = unpack("<hB", xvalue)
        result = {
            "temperature": temp / 10,
            "humidity": humi,
        }
    else:
        device_type = None
    if device_type is None:
        if self.report_unknown == "Thermopro":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Thermopro DEVICE: MAC: %s, ADV: %s",
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
