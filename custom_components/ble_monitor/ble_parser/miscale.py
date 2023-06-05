"""Parser for Xiaomi Mi Scale BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_miscale(self, data, source_mac, rssi):
    """Parser for Xiaomi Mi Scales."""
    msg_length = len(data)
    uuid16 = (data[3] << 8) | data[2]

    if msg_length == 14 and uuid16 == 0x181D:  # Mi Scale V1
        device_type = "Mi Scale V1"
        xvalue = data[4:]
        (control_byte, weight) = unpack("<BH7x", xvalue)

        has_impedance = False
        is_stabilized = control_byte & (1 << 5)
        weight_removed = control_byte & (1 << 7)

        if control_byte & (1 << 0):
            weight = weight / 100
            weight_unit = 'lbs'
        elif control_byte & (1 << 4):
            weight = weight / 100
            weight_unit = 'jin'
        else:
            weight = weight / 200
            weight_unit = 'kg'

    elif msg_length == 17 and uuid16 == 0x181B:  # Mi Scale V2
        device_type = "Mi Scale V2"
        xvalue = data[4:]
        (control_byte_1, control_byte_2, impedance, weight) = unpack("<BB7xHH", xvalue)
        has_impedance = control_byte_2 & (1 << 1)
        is_stabilized = control_byte_2 & (1 << 5)
        weight_removed = control_byte_2 & (1 << 7)

        if control_byte_2 & (1 << 6):
            # measurement in Chinese Catty unit
            weight = weight / 100
            weight_unit = "jin"
        elif control_byte_1 == 3:
            # measurement in lbs
            weight = weight / 100
            weight_unit = "lbs"
        elif control_byte_1 == 2:
            # measurement in kg
            weight = weight / 200
            weight_unit = "kg"
        else:
            # measurement in unknown unit
            weight = weight / 100
            weight_unit = None
    else:
        device_type = None

    if device_type is None:
        if self.report_unknown == "Mi Scale":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Mi Scale DEVICE: MAC: %s, ADV: %s",
                to_mac(source_mac),
                data.hex()
            )
        return None

    result = {
        "non-stabilized weight": weight,
        "weight unit": weight_unit,
        "weight removed": 0 if weight_removed == 0 else 1,
        "stabilized": 0 if is_stabilized == 0 else 1
    }

    if device_type == "Mi Scale V1":
        if is_stabilized and not weight_removed:
            result.update({"weight": weight})
    elif device_type == "Mi Scale V2":
        if is_stabilized and (weight_removed == 0):
            result.update({"stabilized weight": weight})
            if has_impedance:
                result.update({"weight": weight})
                result.update({"impedance": impedance})
    else:
        pass

    firmware = device_type
    miscale_mac = source_mac

    # Check for duplicate messages
    packet_id = xvalue.hex()
    try:
        prev_packet = self.lpacket_ids[miscale_mac]
    except KeyError:
        # start with empty first packet
        prev_packet = None
    if prev_packet == packet_id:
        # only process new messages
        if self.filter_duplicates is True:
            return None
    self.lpacket_ids[miscale_mac] = packet_id
    if prev_packet is None:
        if self.filter_duplicates is True:
            # ignore first message after a restart
            return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and miscale_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(miscale_mac))
        return None

    result.update({
        "type": device_type,
        "firmware": firmware,
        "mac": to_unformatted_mac(miscale_mac),
        "packet": packet_id,
        "rssi": rssi,
        "data": True,
    })
    return result
