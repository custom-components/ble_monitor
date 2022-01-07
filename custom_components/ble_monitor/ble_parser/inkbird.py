"""Parser for Inkbird BLE advertisements"""
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def parse_inkbird(self, data, source_mac, rssi):
    # check for adstruc length
    msg_length = len(data)
    firmware = "Inkbird"
    result = {"firmware": firmware}
    if msg_length == 11:
        device_type = "IBS-TH2"
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
    elif msg_length == 16:
        device_type = "iBBQ-2"
        inkbird_mac = data[6:12]
        xvalue = data[12:16]
        if inkbird_mac != source_mac:
            _LOGGER.debug(
                "Inkbird MAC address doesn't match data MAC address. Data: %s",
                data.hex()
            )
            return None
        (temp_1, temp_2) = unpack("<HH", xvalue)
        if temp_1 < 60000:
            temperature_1 = temp_1 / 10.0
        else:
            temperature_1 = 0
        if temp_2 < 60000:
            temperature_2 = temp_2 / 10.0
        else:
            temperature_2 = 0
        result.update(
            {
                "temperature probe 1": temperature_1,
                "temperature probe 2": temperature_2,
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
    if self.discovery is False and inkbird_mac.lower() not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(inkbird_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in inkbird_mac[:]),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result


def to_mac(addr: int):
    """Convert MAC address."""
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
