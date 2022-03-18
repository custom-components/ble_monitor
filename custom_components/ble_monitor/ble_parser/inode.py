"""Parser for iNode BLE advertisements"""
import logging
import math
from struct import unpack

_LOGGER = logging.getLogger(__name__)

INODE_CARE_SENSORS_IDS = {
    0x82: "iNode Energy Meter",
    0x91: "iNode Care Sensor 1",
    0x92: "iNode Care Sensor 2",
    0x93: "iNode Care Sensor 3",
    0x94: "iNode Care Sensor 4",
    0x95: "iNode Care Sensor 5",
    0x96: "iNode Care Sensor 6",
    0x9A: "iNode Care Sensor T",
    0x9B: "iNode Care Sensor HT",
    0x9C: "iNode Care Sensor PT",
    0x9D: "iNode Care Sensor PHT"
}

MEASUREMENTS = {
    0x91: ["position", "temperature"],
    0x92: ["position", "temperature"],
    0x93: ["position", "temperature", "humidity"],
    0x94: ["position", "temperature"],
    0x95: ["position", "temperature", "magnetic field"],
    0x96: ["position", "temperature"],
    0x9A: ["temperature"],
    0x9B: ["temperature", "humidity"],
    0x9C: ["pressure", "temperature"],
    0x9D: ["pressure", "temperature", "humidity"],
}


def adj_acc(acc):
    if(acc & 0x10) == 0x10:
        acc = -1 * (32 - acc)
    return acc


def parse_inode(self, data, source_mac, rssi):
    """iNode parser"""
    msg_length = len(data)
    firmware = "iNode"
    inode_mac = source_mac
    device_id = data[3]
    xvalue = data[4:]
    result = {"firmware": firmware}
    # Advertisement structure information https://docs.google.com/document/d/1hcBpZ1RSgHRL6wu4SlTq2bvtKSL5_sFjXMu_HRyWZiQ
    if msg_length == 15 and device_id == 0x82:
        """iNode Energy Meter"""
        (raw_avg, raw_sum, options, battery_light, week_day_data) = unpack("<HIHBH", xvalue)
        # Average of previous minute (avg) and sum (sum)
        unit = (options >> 14) & 3
        constant = options & 0x3FFF
        if unit == 0:
            power_unit = "W"
            energy_unit = "kWh"
            constant = constant if constant > 0 else 100
        elif unit == 1:
            power_unit = "m3"
            energy_unit = "m3"
            constant = constant if constant > 0 else 1000
        else:
            power_unit = "cnt"
            energy_unit = "cnt"
            constant = constant if constant > 0 else 1
        power = 1000 * 60 * raw_avg / constant
        energy = raw_sum / constant

        # Battery in % and voltage level in V
        battery = (battery_light >> 4) & 0x0F
        if battery == 1:
            battery_level = 100
        else:
            battery_level = 10 * (min(battery, 11) - 1)
        battery_voltage = (battery_level - 10) * 1.2 / 100 + 1.8

        # Light level in %
        light_level = (battery_light & 0x0F) * 100 / 15

        # Previous day of the week (weekDay) and total for the previous day (weekDayTotal)
        week_day = week_day_data >> 13
        week_day_total = week_day_data & 0x1FFF

        result.update(
            {
                "energy": energy,
                "energy unit": energy_unit,
                "power": power,
                "power unit": power_unit,
                "constant": constant,
                "battery": battery_level,
                "voltage": battery_voltage,
                "light level": light_level,
                "week day": week_day,
                "week day total": week_day_total
            }
        )
    elif msg_length == 26 and device_id in INODE_CARE_SENSORS_IDS:
        # iNode Care Sensors
        measurements = MEASUREMENTS[device_id]
        (
            groups_battery,
            alarm,
            raw_p,
            raw_t,
            raw_h,
            raw_time1,
            raw_time2,
            signature
        ) = unpack("<HHHHHHHQ", xvalue)

        if "temperature" in measurements:
            if device_id in [0x91, 0x94, 0x95, 0x96]:
                temp = raw_t
                if temp > 127:
                    temp = temp - 8192
                temp = max(min(temp, 70), -30)
            elif device_id in [0x92, 0x9A]:
                msb = raw_t[0]
                lsb = raw_t[1]
                temp = msb * 0.0625 + 16 * (lsb & 0x0F)
                if lsb & 0x10:
                    temp = temp - 256
                temp = max(min(temp, 70), -30)
            elif device_id in [0x93, 0x9B, 0x9D]:
                temp = (175.72 * raw_t * 4 / 65536) - 46.85
                temp = max(min(temp, 70), -30)
            elif device_id == 0x9C:
                temp = 42.5 + raw_t / 480
            else:
                temp = 0
            result.update({"temperature": temp})
        if "humidity" in measurements:
            humi = (125 * raw_h * 4 / 65536) - 6
            humi = max(min(humi, 100), 1)
            result.update({"humidity": humi})
        if "pressure" in measurements:
            pressure = raw_p / 16
            result.update({"pressure": pressure})
        if "magnetic field" in measurements:
            magnetic_field = raw_h
            magnetic_field_direction = data[3] << 4
            result.update({
                "magnetic field": magnetic_field,
                "magnetic field direction": magnetic_field_direction,
            })
        if "position" in measurements:
            motion = raw_p & 0x8000
            acc_x = adj_acc((raw_p >> 10) & 0x1F)
            acc_y = adj_acc((raw_p >> 5) & 0x1F)
            acc_z = adj_acc(raw_p & 0x1F)

            acc = math.sqrt(acc_x ** 2 + acc_y ** 2 + acc_z ** 2)
            result.update({
                "motion": motion,
                "motion timer": motion,
                "acceleration": acc,
                "acceleration x": acc_x,
                "acceleration y": acc_y,
                "acceleration z": acc_z
            })

        # Alarm (not used in output)
        move_accelerometer = alarm >> 1
        level_accelerometer = alarm >> 2
        level_temperature = alarm >> 3
        level_humidity = alarm >> 4
        contact_change = alarm >> 5
        move_stopped = alarm >> 6
        move_gtimer = alarm > 7
        level_accelerometer_change = alarm >> 8
        level_magnet_change = alarm >> 9
        level_magnet_timer = alarm >> 10

        # Time (not used in output)
        t_1 = raw_time1 << 16
        t_2 = raw_time2
        time = t_1 | t_2

        # Battery in % and voltage level in V
        battery = (groups_battery >> 12) & 0x0F
        if battery == 1:
            battery_level = 100
        else:
            battery_level = 10 * (min(battery, 11) - 1)
        battery_voltage = (battery_level - 10) * 1.2 / 100 + 1.8
        result.update(
            {
                "battery": battery_level,
                "voltage": battery_voltage,
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
    device_type = INODE_CARE_SENSORS_IDS[device_id]

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
    if self.discovery is False and inode_mac not in self.sensor_whitelist:
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
    """Return formatted MAC address"""
    return ':'.join(f'{i:02X}' for i in addr)
