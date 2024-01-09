"""Parser for Xiaogui Scale BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_xiaogui(self, data: bytes, mac: str):
    """Xiaogui Scales parser"""
    msg_length = len(data)

    if msg_length == 17:
        firmware = "Xiaogui"
        xiaogui_mac = data[11:]

        if xiaogui_mac != mac:
            _LOGGER.error("Xiaogui MAC address doesn't match data MAC address. Data: %s", data.hex())
            return None

        result = {
            "firmware": firmware,
            "mac": to_unformatted_mac(xiaogui_mac),
            "data": True,
        }

        xvalue = data[3:11]
        (frame_cnt, weight, impedance, control, stablilized_byte) = unpack(">BHHHB", xvalue)
        packet_id = frame_cnt << 8 | stablilized_byte

        result.update({"packet": packet_id})

        if stablilized_byte == 0x20:
            device_type = "TZC4"
            result.update({"non-stabilized weight": weight / 10})
            result.update({"weight unit": "kg"})
            result.update({"stabilized": 0})
        elif stablilized_byte == 0x21:
            device_type = "TZC4"
            result.update({"non-stabilized weight": weight / 10})
            result.update({"weight": weight / 10})
            result.update({"weight unit": "kg"})
            result.update({"impedance": impedance / 10})
            result.update({"stabilized": 1})
        elif stablilized_byte == 0x24:
            device_type = "QJ-J"
            result.update({"non-stabilized weight": weight / 100})
            result.update({"weight unit": "kg"})
            result.update({"stabilized": 0})
        elif stablilized_byte == 0x25:
            device_type = "QJ-J"
            result.update({"non-stabilized weight": weight / 100})
            result.update({"weight": weight / 100})
            result.update({"weight unit": "kg"})
            result.update({"impedance": impedance / 10})
            result.update({"stabilized": 1})
        else:
            _LOGGER.error(
                "Stabilized byte of Xiaogui scale is reporting a new value, "
                "please report an issue to the developers with this error: Payload is %s",
                data.hex()
            )
            device_type = None
    else:
        device_type = None

    if device_type is None:
        if self.report_unknown == "Xiaogui":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Xiaogui DEVICE: MAC: %s, ADV: %s",
                to_mac(mac),
                data.hex()
            )
        return None
    else:
        result.update({"type": device_type})

    # Check for duplicate messages
    try:
        prev_packet = self.lpacket_ids[mac]
    except KeyError:
        # start with empty first packet
        prev_packet = None
    if prev_packet == packet_id:
        # only process new messages
        return None
    self.lpacket_ids[mac] = packet_id

    return result
