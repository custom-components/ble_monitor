"""Parser for BlueMaestro BLE advertisements."""
import logging
from struct import unpack

from .helpers import (
    to_mac,
    to_unformatted_mac,
)

_LOGGER = logging.getLogger(__name__)


def parse_bluemaestro(self, data, source_mac, rssi):
    """Parse BlueMaestro advertisement."""
    msg_length = len(data)
    firmware = "BlueMaestro"
    device_id = data[4]
    bluemaestro_mac = source_mac
    msg = data[5:]
    if msg_length == 18 and device_id in [0x16, 0x17]:
        # BlueMaestro Tempo Disc THD
        device_type = "Tempo Disc THD"
        # pylint: disable=unused-variable
        (batt, time_interval, log_cnt, temp, humi, dew_point, mode) = unpack("!BhhhHhH", msg)
        result = {
            "temperature": temp / 10,
            "humidity": humi / 10,
            "battery": batt,
            "dewpoint": dew_point / 10
        }
    elif msg_length == 18 and device_id == 0x1b:
        # BlueMaestro Tempo Disc THPD (sends P instead of D, no D is sent)
        device_type = "Tempo Disc THPD"
        # pylint: disable=unused-variable
        (batt, time_interval, log_cnt, temp, humi, press, mode) = unpack("!BhhhHhH", msg)
        result = {
            "temperature": temp / 10,
            "humidity": humi / 10,
            "battery": batt,
            "pressure": press / 10
        }
    elif msg_length == 22 and device_id == 0x01:
        # BlueMaestro Pebble
        device_type = "Pebble"
        # pylint: disable=unused-variable
        (temp_1, temp_2, temp_3, humi, press) = unpack(
            "<hhhBH", msg[0:9]
        )
        log_cnt = "no packet id"
        result = {
            "temperature": temp_2 / 10,
            "humidity": humi,
            "pressure": press,
        }
    else:
        if self.report_unknown == "BlueMaestro":
            _LOGGER.info(
                "BLE ADV from UNKNOWN BlueMaestro DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in whitelist, if needed
    if self.discovery is False and bluemaestro_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(bluemaestro_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": to_unformatted_mac(bluemaestro_mac),
        "type": device_type,
        "packet": log_cnt,
        "firmware": firmware,
        "data": True
    })
    return result
