"""Parser for Moat BLE advertisements"""
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def parse_moat(self, data, source_mac, rssi):
    """Parser for Moat sensors"""
    msg_length = len(data)
    firmware = "Moat"
    moat_mac = source_mac
    device_id = (data[3] << 8) | data[2]
    result = {"firmware": firmware}
    if msg_length == 22 and device_id == 0x1000:
        device_type = "Moat S2"
        (temp, humi, volt) = unpack("<HHH", data[14:20])
        temperature = -46.85 + 175.72 * temp / 65536.0
        humidity = -6.0 + 125.0 * humi / 65536.0
        voltage = volt / 1000
        if volt >= 3000:
            batt = 100
        elif volt >= 2900:
            batt = 42 + (volt - 2900) * 0.58
        elif volt >= 2740:
            batt = 18 + (volt - 2740) * 0.15
        elif volt >= 2440:
            batt = 6 + (volt - 2440) * 0.04
        elif volt >= 2100:
            batt = (volt - 2100) * (6 / 340)
        else:
            batt = 0
        result.update({
            "temperature": round(temperature, 3),
            "humidity": round(humidity, 3),
            "voltage": voltage,
            "battery": round(batt, 1)
        })
    else:
        if self.report_unknown == "Moat":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Moat DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in whitelist, if needed
    if self.discovery is False and moat_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(moat_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in moat_mac[:]),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result


def to_mac(addr: int):
    """Return formatted MAC address"""
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
