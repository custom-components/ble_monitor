"""Parser for Chef iQ BLE advertisements."""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_chefiq(self, data: str, mac: bytes):
    """Parse Chef iQ advertisement."""
    msg_length = len(data)
    firmware = "Chef iQ"
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
                "BLE ADV from UNKNOWN Chef iQ DEVICE: MAC: %s, ADV: %s",
                to_mac(mac),
                data.hex()
            )
        return None

    result.update({
        "mac": to_unformatted_mac(mac),
        "type": device_type,
        "packet": log_cnt,
        "firmware": firmware,
        "data": True
    })
    return result
