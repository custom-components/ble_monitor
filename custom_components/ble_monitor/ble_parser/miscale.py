# Parser for Xiaomi Mi Scale BLE advertisements
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def parse_miscale(self, data, source_mac, rssi):
    # check for adstruc length
    msg_length = len(data)
    uuid16 = (data[3] << 8) | data[2]

    if msg_length == 14 and uuid16 == 0x181D:  # Mi Scale V1
        device_type = "Mi Scale V1"
        xvalue = data[4:]
        (controlByte, weight) = unpack("<BH7x", xvalue)

        hasImpedance = False
        isStabilized = controlByte & (1 << 5)
        weightRemoved = controlByte & (1 << 7)

        if controlByte & (1 << 0):
            weight = weight / 100
            weight_unit = 'lbs'
        elif controlByte & (1 << 4):
            weight = weight / 100
            weight_unit = 'jin'
        else:
            weight = weight / 200
            weight_unit = 'kg'

    elif msg_length == 17 and uuid16 == 0x181B:  # Mi Scale V2
        device_type = "Mi Scale V2"
        xvalue = data[4:]
        (measunit, controlByte, impedance, weight) = unpack("<BB7xHH", xvalue)
        hasImpedance = controlByte & (1 << 1)
        isStabilized = controlByte & (1 << 5)
        weightRemoved = controlByte & (1 << 7)

        if measunit & (1 << 4):
            # measurement in Chinese Catty unit
            weight = weight / 100
            weight_unit = "jin"
        elif measunit == 3:
            # measurement in lbs
            weight = weight / 100
            weight_unit = "lbs"
        elif measunit == 2:
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
        "weight removed": 0 if weightRemoved == 0 else 1,
        "stabilized": 0 if isStabilized == 0 else 1
    }

    if isStabilized and not weightRemoved:
        result.update({"weight": weight})

    if hasImpedance:
        result.update({"impedance": impedance})

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
    if self.discovery is False and miscale_mac.lower() not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(miscale_mac))
        return None

    result.update({
        "type": device_type,
        "firmware": firmware,
        "mac": ''.join('{:02X}'.format(x) for x in miscale_mac),
        "packet": packet_id,
        "rssi": rssi,
        "data": True,
    })
    return result


def to_mac(addr: int):
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
