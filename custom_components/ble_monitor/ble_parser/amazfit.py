"""Parser for Amazfit BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_amazfit(self, service_data: str, man_spec_data: str, mac: str):
    """parser for Amazfit scale and Miband 4 and 5"""
    if service_data:
        service_data_length = len(service_data)
    else:
        service_data_length = 0
    if man_spec_data:
        man_spec_data_length = len(man_spec_data)
    else:
        man_spec_data_length = 0

    result = {}

    if service_data_length == 24:
        device_type = "Amazfit Smart Scale"
        firmware = "Amazfit"
        xvalue = service_data[4:25]
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
            result.update({
                "non-stabilized weight": weight / 200,
                "stabilized": 0,
                "weight unit": 'kg',
            })
        else:
            result.update({
                "non-stabilized weight": weight / 200,
                "stabilized": 1,
                "weight": weight / 200,
                "impedance": impedance / 10,
                "pulse": pulse,
                "weight unit": 'kg',
            })
    elif man_spec_data_length == 28:
        device_type = "Mi Band"
        firmware = "Mi Band"
        heart_rate = man_spec_data[7]
        if heart_rate != 0xFF:
            result.update({
                "heart rate": heart_rate
            })
        if service_data_length == 8:
            (steps,) = unpack("I", service_data[4:])
            result.update({
                "steps": steps
            })
    else:
        if self.report_unknown == "Amazfit":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Amazfit Scale DEVICE: MAC: %s, service data: %s, manufacturer data: %s",
                to_mac(mac),
                service_data,
                man_spec_data
            )
        return None

    result.update({
        "type": device_type,
        "firmware": firmware,
        "mac": to_unformatted_mac(mac),
        "packet": 'no packet id',
        "data": True,
    })
    return result
