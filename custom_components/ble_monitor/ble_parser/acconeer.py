"""Parser for Acconeer BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)

ACCONEER_SENSOR_IDS = {
    0x80: "Acconeer XM122",
    0x90: "Acconeer XM126",
    0x91: "Acconeer XM126",
}


def parse_acconeer(self, data: bytes, mac: bytes):
    """Acconeer parser"""
    msg_length = len(data)
    firmware = "Acconeer"
    device_id = data[4]
    xvalue = data[5:]
    result = {"firmware": firmware}

    if msg_length == 19 and device_id in ACCONEER_SENSOR_IDS:
        # Acconeer Sensors
        device_type = ACCONEER_SENSOR_IDS[device_id]

        if device_id == 0x90:
            (
                battery_level,
                temperature,
                distance_mm,
                reserved2
            ) = unpack("<HhHQ", xvalue)
            result.update({
                "distance mm": distance_mm,
                "temperature": temperature,
                "battery": battery_level,
            })
        else:
            (
                battery_level,
                temperature,
                presence,
                reserved2
            ) = unpack("<HhHQ", xvalue)
            result.update({
                "motion": 0 if presence == 0 else 1,
                "temperature": temperature,
                "battery": battery_level,
            })
    else:
        device_type = None

    if device_type is None:
        if self.report_unknown == "Acconeer":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Acconeer DEVICE: MAC: %s, ADV: %s",
                to_mac(mac),
                data.hex()
            )
        return None

    # Check for duplicate messages
    packet_id = xvalue.hex()
    try:
        prev_packet = self.lpacket_ids[mac]
    except KeyError:
        # start with empty first packet
        prev_packet = None
    if prev_packet == packet_id:
        # only process new messages
        if self.filter_duplicates is True:
            return None
    self.lpacket_ids[mac] = packet_id

    result.update({
        "mac": to_unformatted_mac(mac),
        "type": device_type,
        "packet": packet_id,
        "firmware": firmware,
        "data": True
    })
    return result
