"""Parser for Switchbot BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_switchbot(self, data: bytes, mac: bytes):
    """Switchbot parser"""
    msg_length = len(data)
    device_id = data[4]

    if msg_length == 10 and device_id in [0x54, 0x69]:
        xvalue = data[6:10]
        (batt, temp_frac, temp_int, humi) = unpack("<BBBB", xvalue)
        batt = (batt & 127)

        temp_sign = temp_int & 128
        temp = float(temp_int & 127) + float((temp_frac & 15) / 10.0)
        if temp_sign == 0:
            # Negative temperature
            temp = -1 * temp

        humi = (humi & 127)
        if device_id == 0x54:
            device_type = "Meter TH S1"
        elif device_id == 0x69:
            device_type = "Meter TH plus"
        else:
            device_type = "unknown"
        firmware = "Switchbot"
        result = {
            "temperature": temp,
            "humidity": humi,
            "battery": batt
        }
    else:
        device_type = "unknown"

    if device_type == "unknown":
        if self.report_unknown == "Switchbot":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Switchbot DEVICE: MAC: %s, ADV: %s",
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
