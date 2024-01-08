"""Parser for Chef iQ BLE advertisements."""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_chefiq(self, data, source_mac):
    """Parse Chef iQ advertisement."""
    msg_length = len(data)
    firmware = "Chef iQ"
    chefiq_mac = source_mac
    msg = data[6:]
    if msg_length == 22:
        # Chef iQ CQ60
        device_type = "CQ60"
        (batt, temp_probe_3, _, temp_meat, temp_tip, temp_probe_1, temp_probe_2, temp_ambient, _) = unpack(
            "<BBHHHHHHh", msg
        )
        log_cnt = "no packet id"
        result = {
            "battery": batt,
            "meat temperature": temp_meat / 10,
            "temperature probe tip": temp_tip / 10,
            "temperature probe 1": temp_probe_1 / 10,
            "temperature probe 2": temp_probe_2 / 10,
            "temperature probe 3": temp_probe_3,
            "ambient temperature": temp_ambient / 10,
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
        "mac": to_unformatted_mac(chefiq_mac),
        "type": device_type,
        "packet": log_cnt,
        "firmware": firmware,
        "data": True
    })
    return result
