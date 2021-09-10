# Parser for Moat BLE advertisements
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def parse_moat(self, data, source_mac, rssi):
    # check for adstruc length
    msg_length = len(data)
    firmware = "Moat"
    moat_mac = source_mac
    device_id = (data[3] << 8) | data[2]
    result = {"firmware": firmware}
    if msg_length == 22 and device_id == 0x1000:
        print(data[14:20].hex())
        device_type = "Moat S2"
        (temp, humi, volt) = unpack("<HHH", data[14:20])
        temperature = -46.85 + 175.72 * temp / 65536.0
        humidity = -6.0 + 125.0 * humi / 65536.0
        voltage = volt / 1000
        if volt >= 3000:
            batt = 100
        elif volt >= 2600:
            batt = 60 + (volt - 2600) * 0.1
        elif volt >= 2500:
            batt = 40 + (volt - 2500) * 0.2
        elif volt >= 2450:
            batt = 20 + (volt - 2450) * 0.4
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
    if self.discovery is False and moat_mac.lower() not in self.whitelist:
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
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
