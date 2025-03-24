"""Parser for Thermopro BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_thermopro(self, data: bytes, device_type, mac: bytes):
    """Thermopro parser"""
    if device_type in ["TP357", "TP359"]:
        firmware = "Thermopro"
        xvalue = data[3:7]
        (temp, humi, batt) = unpack("<hBB", xvalue)
        if batt == 2:
            # full battery
            batt_low = 0
        else:
            # low battery
            batt_low = 1
        result = {
            "temperature": temp / 10,
            "humidity": humi,
            "battery low": batt_low
        }
    else:
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
