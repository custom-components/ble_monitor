"""Parser for Switchbot BLE advertisements"""
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def parse_switchbot(self, data, source_mac, rssi):
    """Switchbot parser"""
    msg_length = len(data)
    switchbot_mac = source_mac

    if msg_length == 10:
        xvalue = data[6:10]
        (byte1, byte2, byte3, byte4) = unpack("<BBBB", xvalue)
        batt = (byte1 & 127)
        temp = float(byte3 - 128) + float(byte2 / 10.0)
        humi = byte4
        device_type = "Meter TH S1"
        firmware = "Switchbot"
        result = {
            "temperature": temp,
            "humidity": humi,
            "battery": batt
        }
    else:
        if self.report_unknown == "Switchbot":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Switchbot DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and switchbot_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(switchbot_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join(f'{i:02X}' for i in switchbot_mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result


def to_mac(addr: int):
    """Return formatted MAC address"""
    return ':'.join(f'{i:02X}' for i in addr)
