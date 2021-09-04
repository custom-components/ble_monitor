# Parser for Thermoplus BLE advertisements
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def parse_thermoplus(self, data, source_mac, rssi):
    # check for adstruc length
    msg_length = len(data)
    if msg_length == 22:
        device_id = data[2]
        if device_id == 0x10:
            device_type = "Lanyard/mini hygrometer"
        elif device_id == 0x11:
            device_type = "Smart hygrometer"
        else:
            device_type = None
        firmware = "Thermoplus"

        thermoplus_mac_reversed = data[6:12]
        thermoplus_mac = thermoplus_mac_reversed[::-1]

        xvalue = data[12:18]
        (volt, temp, humi) = unpack("<HhH", xvalue)
        batt = 2500
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
        result = {
            "voltage": volt / 1000,
            "temperature": temp / 16,
            "humidity": humi / 16,
            "battery": batt
        }
    else:
        device_type = None
    if device_type is None:
        if self.report_unknown == "Thermoplus":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Thermoplus DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in message and in service data
    if thermoplus_mac != source_mac:
        _LOGGER.debug("Invalid MAC address for Thermoplus device")
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and thermoplus_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(thermoplus_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in thermoplus_mac[:]),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result


def to_mac(addr: int):
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
