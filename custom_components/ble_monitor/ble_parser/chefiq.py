"""Parser for Chef iQ BLE advertisements."""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_chefiq(self, data, source_mac, rssi):
    """Parse Chef iQ advertisement."""
    msg_length = len(data)
    firmware = "Chef iQ"
    chefiq_mac = source_mac
    msg = data[6:]
    if msg_length == 22:
        # Chef iQ CQ60
        device_type = "CQ60"
        (batt, temp_1, temp_2, temp_3, temp_4, temp_5, temp_6, temp_7, humi) = unpack(
            "<BBHHHHHHh", msg
        )
        log_cnt = "no packet id"
        result = {
            "battery": batt,
            "temperature": temp_1,
            "temperature probe 1": temp_2 / 10,
            "temperature probe 2": temp_3 / 10,
            "temperature probe 3": temp_4 / 10,
            "temperature probe 4": temp_5 / 10,
            "temperature probe 5": temp_6 / 10,
            "temperature probe 6": temp_7 / 10,
            "humidity": humi / 100,
        }
    else:
        if self.report_unknown == "Chef iQ":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Chef iQ DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in whitelist, if needed
    if self.discovery is False and chefiq_mac not in self.sensor_whitelist:
        _LOGGER.debug(
            "Discovery is disabled. MAC: %s is not whitelisted!",
            to_mac(chefiq_mac)
        )
        return None

    result.update({
        "rssi": rssi,
        "mac": to_unformatted_mac(chefiq_mac),
        "type": device_type,
        "packet": log_cnt,
        "firmware": firmware,
        "data": True
    })
    return result
