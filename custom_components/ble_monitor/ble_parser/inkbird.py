"""Parser for Inkbird BLE advertisements"""
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def convert_temperature(temp):
    """Temperature converter"""
    if temp > 0:
        temperature = temp / 10.0
    else:
        temperature = 0
    return temperature


def parse_inkbird(self, data, source_mac, rssi):
    """Inkbird parser"""
    msg_length = len(data)
    firmware = "Inkbird"
    result = {"firmware": firmware}
    if msg_length == 11:
        device_type = "IBS-TH"
        inkbird_mac = source_mac
        xvalue = data[2:10]
        (temp, hum) = unpack("<hH", xvalue[0:4])
        bat = int.from_bytes(xvalue[7:8], 'little')
        result.update(
            {
                "temperature": temp / 100,
                "humidity": hum / 100,
                "battery": bat,
            }
        )
    elif msg_length == 14:
        device_type = "iBBQ-1"
        inkbird_mac = data[6:12]
        xvalue = data[12:14]
        if source_mac not in [inkbird_mac, inkbird_mac[::-1]]:
            _LOGGER.debug(
                "Inkbird MAC address doesn't match data MAC address. Data: %s",
                data.hex()
            )
            return None
        (temp_1,) = unpack("<h", xvalue)
        result.update(
            {
                "temperature probe 1": convert_temperature(temp_1),
            }
        )
    elif msg_length == 16:
        device_type = "iBBQ-2"
        inkbird_mac = data[6:12]
        xvalue = data[12:16]
        if source_mac not in [inkbird_mac, inkbird_mac[::-1]]:
            _LOGGER.debug(
                "Inkbird MAC address doesn't match data MAC address. Data: %s",
                data.hex()
            )
            return None
        (temp_1, temp_2) = unpack("<HH", xvalue)
        result.update(
            {
                "temperature probe 1": convert_temperature(temp_1),
                "temperature probe 2": convert_temperature(temp_2),
            }
        )
    elif msg_length == 20:
        inkbird_mac = data[6:12]
        xvalue = data[12:20]
        if source_mac not in [inkbird_mac, inkbird_mac[::-1]]:
            _LOGGER.debug(
                "Inkbird MAC address doesn't match data MAC address. Data: %s",
                data.hex()
            )
            return None
        device_type = "iBBQ-4"
        (temp_1, temp_2, temp_3, temp_4) = unpack("<hhhh", xvalue)
        result.update(
            {
                "temperature probe 1": convert_temperature(temp_1),
                "temperature probe 2": convert_temperature(temp_2),
                "temperature probe 3": convert_temperature(temp_3),
                "temperature probe 4": convert_temperature(temp_4),
            }
        )
    elif msg_length == 24:
        inkbird_mac = data[6:12]
        xvalue = data[12:24]
        if source_mac not in [inkbird_mac, inkbird_mac[::-1]]:
            _LOGGER.debug("Inkbird MAC address doesn't match data MAC address. Data: %s", data.hex())
            return None
        device_type = "iBBQ-6"
        (temp_1, temp_2, temp_3, temp_4, temp_5, temp_6) = unpack("<hhhhhh", xvalue)
        result.update(
            {
                "temperature probe 1": convert_temperature(temp_1),
                "temperature probe 2": convert_temperature(temp_2),
                "temperature probe 3": convert_temperature(temp_3),
                "temperature probe 4": convert_temperature(temp_4),
                "temperature probe 5": convert_temperature(temp_5),
                "temperature probe 6": convert_temperature(temp_6),
            }
        )
    else:
        if self.report_unknown == "Inkbird":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Inkbird DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and source_mac.lower() not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(source_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in source_mac[:]),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result


def to_mac(addr: int):
    """Convert MAC address."""
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
