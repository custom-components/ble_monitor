"""Parser for Xiaogui Scale BLE advertisements"""
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def parse_xiaogui(self, data, source_mac, rssi):
    """Xiaogui Scales parser"""
    msg_length = len(data)

    if msg_length == 17:
        firmware = "Xiaogui"
        device_type = "TZC4"
        xiaogui_mac = data[11:]

        if xiaogui_mac != source_mac:
            _LOGGER.error("Xiaogui MAC address doesn't match data MAC address. Data: %s", data.hex())
            return None

        result = {
            "firmware": firmware,
            "type": device_type,
            "mac": ''.join('{:02X}'.format(x) for x in xiaogui_mac),
            "rssi": rssi,
            "data": True,
        }

        xvalue = data[3:11]
        (frame_cnt, weight, impedance, control, stablilized_byte) = unpack(">BHHHB", xvalue)
        packet_id = frame_cnt << 8 | stablilized_byte

        result.update({"packet": packet_id})

        if stablilized_byte == 0x20:
            result.update({"non-stabilized weight": weight / 10})
            result.update({"weight unit": "kg"})
            result.update({"stabilized": 0})
        elif stablilized_byte == 0x21:
            result.update({"non-stabilized weight": weight / 10})
            result.update({"weight": weight / 10})
            result.update({"weight unit": "kg"})
            result.update({"impedance": impedance / 10})
            result.update({"stabilized": 1})
        else:
            _LOGGER.error(
                "Stabilized byte of Xiaogui scale is reporting a new value, "
                "please report an issue to the developers with this error: Payload is %s",
                data.hex()
            )
            result.update({"data": False})
    else:
        device_type = None
    if device_type is None:
        if self.report_unknown == "Xiaogui":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Xiaogui DEVICE: MAC: %s, ADV: %s",
                to_mac(source_mac),
                data.hex()
            )
        return None

    # Check for duplicate messages
    try:
        prev_packet = self.lpacket_ids[xiaogui_mac]
    except KeyError:
        # start with empty first packet
        prev_packet = None
    if prev_packet == packet_id:
        # only process new messages
        return None
    self.lpacket_ids[xiaogui_mac] = packet_id

    # check for MAC presence in whitelist, if needed
    if self.discovery is False and xiaogui_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(xiaogui_mac))
        return None

    return result


def to_mac(addr: int):
    """Return formatted MAC address"""
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
