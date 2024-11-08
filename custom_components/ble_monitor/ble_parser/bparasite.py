"""Parser for BParasite BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_bparasite(self, data: bytes, mac: bytes):
    """Check for adstruc length"""
    msg_length = len(data)
    if msg_length == 22:  # TODO: Use protocol bits?
        device_type = "b-parasite V1.1.0"
        firmware = "b-parasite V1.1.0 (with illuminance)"
        (protocol, packet_id, batt, temp, humi, moist, bpara_mac, light) = unpack(">BBHhHH6sH", data[4:])
        result = {
            "temperature": temp / (100 if (protocol >> 4) == 2 else 1000),
            "humidity": (humi / 65536) * 100,
            "voltage": batt / 1000.0,
            "moisture": (moist / 65536) * 100,
            "illuminance": light,
            "data": True
        }
    elif msg_length == 20:
        device_type = "b-parasite V1.0.0"
        firmware = "b-parasite V1.0.0 (without illuminance)"
        (protocol, packet_id, batt, temp, humi, moist, bpara_mac) = unpack(">BBHhHH6s", data[4:])
        result = {
            "temperature": temp / (100 if (protocol >> 4) == 2 else 1000),
            "humidity": (humi / 65536) * 100,
            "voltage": batt / 1000.0,
            "moisture": (moist / 65536) * 100,
            "data": True
        }
    else:
        if self.report_unknown == "b-parasite":
            _LOGGER.info(
                "BLE ADV from UNKNOWN b-parasite DEVICE: MAC: %s, AdStruct(%d): %s",
                to_mac(mac),
                msg_length,
                data.hex()
            )
        return None

    try:
        prev_packet = self.lpacket_ids[mac]
    except KeyError:
        # start with empty first packet
        prev_packet = None

    if self.filter_duplicates is True:
        # only process messages with same priority that have a changed packet id
        if prev_packet == packet_id:
            return None

    self.lpacket_ids[mac] = packet_id

    result.update({
        "mac": to_unformatted_mac(mac),
        "type": device_type,
        "packet": packet_id,
        "firmware": firmware,
    })

    return result
