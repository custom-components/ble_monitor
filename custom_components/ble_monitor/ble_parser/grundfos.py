"""Parser for Grundfos BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


PUMP_MODE_DICT = {
    0: "Constant speed level 3",
    1: "Constant speed level 2",
    2: "Constant speed level 1",
    3: "Autoadapt",
    4: "Proportional pressure level 1",
    5: "Proportional pressure level 2",
    6: "Proportional pressure level 3",
    7: "Constant differential pressure level 1",
    8: "Constant differential pressure level 2",
    9: "Constant differential pressure level 1",
}


def parse_grundfos(self, data: str, mac: bytes):
    """Grundfos parser"""
    device_type = "MI401"
    firmware = "Grundfos"

    xvalue = data[6:17]
    (packet, bat_status, pump_id, flow, press, pump_mode, temp) = unpack(
        "<BBHHhxBB", xvalue
    )
    pump_mode = PUMP_MODE_DICT[pump_mode]

    result = {
        "packet": packet,
        "flow": round(flow / 6.5534, 1),
        "water pressure": round(press / 32767, 3),
        "temperature": temp,
        "pump mode": pump_mode,
        "pump id": pump_id,
        "battery status": bat_status,
    }

    if self.report_unknown == "Grundfos":
        _LOGGER.info(
            "BLE ADV from UNKNOWN Grundfos DEVICE: MAC: %s, ADV: %s",
            to_mac(mac),
            data.hex()
        )

    result.update({
        "mac": to_unformatted_mac(mac),
        "type": device_type,
        "firmware": firmware,
        "data": True
    })
    return result
