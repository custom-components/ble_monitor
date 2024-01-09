"""Parser for JINOU Beacon BLE advertisements"""
import logging

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_jinou(self, data: bytes, mac: str):
    """Jinou parser"""
    msg_length = len(data)
    firmware = "Jinou"
    result = {"firmware": firmware}
    if msg_length == 15:
        device_type = "BEC07-5"
        temp = float(str(data[3]) + "." + str(data[4]))
        if data[2] == 1:
            temp = temp * -1
        hum = float(str(data[6]) + "." + str(data[7]))

        result.update(
            {
                "temperature": temp,
                "humidity": hum
            }
        )
    else:
        if self.report_unknown == "Jinou":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Jinou DEVICE: MAC: %s, ADV: %s",
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
