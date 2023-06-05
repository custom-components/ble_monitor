"""Parser for Thermopro BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_thermopro(self, data, device_type, source_mac, rssi):
    """Thermopro parser"""
    if device_type in ["TP357", "TP359"]:
        firmware = "Thermopro"
        thermopro_mac = source_mac

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
                "BLE ADV from UNKNOWN Thermopro DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in message and in service data
    if thermopro_mac != source_mac:
        _LOGGER.debug("Invalid MAC address for Thermopro device")
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and thermopro_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(thermopro_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": to_unformatted_mac(thermopro_mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result
