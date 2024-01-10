"""Parser for Hormann BLE advertisements"""
import logging

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_hormann(self, data: str, mac: bytes):
    """Hörmann parser"""
    result = {"firmware": "Hörmann"}

    # Hörmann adv contain two 0xFF manufacturer specific data packets
    packet_start = 0
    data_size = len(data)
    device_type = None

    while data_size > 1:
        packet_size = data[packet_start] + 1
        if packet_size > 1 and packet_size <= data_size:
            packet = data[packet_start:packet_start + packet_size]
            packet_type = packet[1]

            if packet_type == 0xFF and packet_size == 21:
                device_type = "Supramatic E4 BS"
                # garage_door_state = packet[4] & 0x0F
                # not used, as we don't know the exact meaning
                # 0x03: open
                # 0x04: closed
                # 0x05: partially open
                # 0x07: partially open
                opening_percentage = packet[5] / 2

                # Convert state to a string
                if opening_percentage == 0:
                    opening = 0
                else:
                    opening = 1

                # Opening
                result.update({"opening": opening})
                result.update({"opening percentage": opening_percentage})

        data_size -= packet_size
        packet_start += packet_size

    if device_type is None:
        if self.report_unknown == "Hormann":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Hormann DEVICE: MAC: %s, DEVICE TYPE: %s, ADV: %s",
                to_mac(mac),
                device_type,
                data.hex()
            )
        return None

    result.update({
        "mac": to_unformatted_mac(mac),
        "type": device_type,
        "packet": "no packet id",
        "data": True
    })
    return result
