# Parser for iNode BLE advertisements
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def parse_inode(self, data, source_mac, rssi):
    # check for adstruc length
    msg_length = len(data)
    firmware = "iNode"
    inode_mac = source_mac
    device_id = data[3]
    xvalue = data[4:]
    result = {"firmware": firmware}
    if msg_length == 15 and device_id == 0x82:
        device_type = "iNode Energy Meter"
        (rawAvg, rawSum, options, batteryAndLight, weekDayData) = unpack("<HIHBH", xvalue)
        # Average of previous minute (avg) and sum (sum)
        unit = (options >> 14) & 3
        constant = options & 0x3FFF
        if unit == 0:
            powerUnit = "W"
            energyUnit = "kWh"
            constant = constant if constant > 0 else 100
        elif unit == 1:
            powerUnit = "m3"
            energyUnit = "m3"
            constant = constant if constant > 0 else 1000
        else:
            powerUnit = "cnt"
            energyUnit = "cnt"
            constant = constant if constant > 0 else 1
        power = 1000 * 60 * rawAvg / constant
        energy = rawSum / constant

        # Battery in % and voltage level in V
        battery = (batteryAndLight >> 4) & 0x0F
        if battery == 1:
            batteryLevel = 100
        else:
            batteryLevel = 10 * (min(battery, 11) - 1)
        batteryVoltage = (batteryLevel - 10) * 1.2 / 100 + 1.8

        # Light level in %
        lightLevel = (batteryAndLight & 0x0F) * 100 / 15

        # Previous day of the week (weekDay) and total for the previous day (weekDayTotal)
        weekDay = weekDayData >> 13
        weekDayTotal = weekDayData & 0x1FFF

        result.update(
            {
                "energy": energy,
                "energy unit": energyUnit,
                "power": power,
                "power unit": powerUnit,
                "constant": constant,
                "battery": batteryLevel,
                "voltage": batteryVoltage,
                "light level": lightLevel,
                "week day": weekDay,
                "week day total": weekDayTotal
            }
        )
    else:
        if self.report_unknown == "iNode":
            _LOGGER.info(
                "BLE ADV from UNKNOWN iNode DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # Check for duplicate messages
    packet_id = xvalue.hex()
    try:
        prev_packet = self.lpacket_ids[inode_mac]
    except KeyError:
        # start with empty first packet
        prev_packet = None
    if prev_packet == packet_id:
        # only process new messages
        if self.filter_duplicates is True:
            return None
    self.lpacket_ids[inode_mac] = packet_id

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and inode_mac.lower() not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(inode_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in inode_mac[:]),
        "type": device_type,
        "packet": packet_id,
        "firmware": firmware,
        "data": True
    })
    return result


def to_mac(addr: int):
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
