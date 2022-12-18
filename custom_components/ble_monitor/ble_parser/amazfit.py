"""Parser for Amazfit BLE advertisements"""
import logging
from struct import unpack

from .helpers import (
    to_mac,
    to_unformatted_mac,
)

_LOGGER = logging.getLogger(__name__)


def parse_amazfit(self, data, source_mac, rssi):
    """Parse Amazfit BLE advertisements"""
    msg_length = len(data)

    if msg_length == 24:
        device_type = "Amazfit Smart Scale"
        firmware = "Amazfit"
        xvalue = data[4:25]
        # Not all info is known
        # byte 0-4: unknown
        # byte 5-6: impedance / 10
        # byte 7-8: weight / 200
        # byte 9-11: unknown, used now as "if 000000 than non-stabilized weight"
        # byte 12: pulse
        # byte 13: unknown
        # byte 14-19: user information, not used yet
        (impedance, weight, unk_1, unk_2, pulse) = unpack("<5xHHBHB1x6x", xvalue)
        if unk_1 == 0 and unk_2 == 0:
            result = {
                "non-stabilized weight": weight / 200,
                "stabilized": 0,
                "weight unit": 'kg',
            }
        else:
            result = {
                "non-stabilized weight": weight / 200,
                "stabilized": 1,
                "weight": weight / 200,
                "impedance": impedance / 10,
                "pulse": pulse,
                "weight unit": 'kg',
            }
    else:
        if self.report_unknown == "Amazfit":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Amazfit Scale DEVICE: MAC: %s, ADV: %s",
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and source_mac.lower() not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(source_mac))
        return None

    result.update({
        "type": device_type,
        "firmware": firmware,
        "mac": to_unformatted_mac(source_mac),
        "packet": 'no packet id',
        "rssi": rssi,
        "data": True,
    })
    return result
