"""Parser for JINOU Beacon BLE advertisements"""
import logging

from .helpers import (
    to_mac,
    to_unformatted_mac,
)

_LOGGER = logging.getLogger(__name__)


def parse_jinou(self, data, source_mac, rssi):
    """Jinou parser"""
    msg_length = len(data)
    firmware = "Jinou"
    result = {"firmware": firmware}
    if msg_length == 15:
        device_type = "BEC07-5"
        jinou_mac = source_mac
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
                "BLE ADV from UNKNOWN Jinou DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and jinou_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(jinou_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": to_unformatted_mac(jinou_mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result
