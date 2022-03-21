"""Parser for Switchbot BLE advertisements"""
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def parse_switchbot(self, data, source_mac, rssi):
    """Switchbot parser"""
    msg_length = len(data)
    switchbot_mac = source_mac
    device_id = data[4] + (data[5] << 8)

    if msg_length == 10 and device_id in [0x0054, 0x0069]:
        xvalue = data[6:10]
        (byte1, byte2, byte3, byte4) = unpack("<BBBB", xvalue)
        batt = (byte1 & 127)
        temp = float(byte3 - 128) + float(byte2 / 10.0)
        humi = (byte4 & 127)
        if device_id == 0x0054:
            device_type = "Meter TH S1"
        elif device_id == 0x0069:
            device_type = "Meter TH plus"
        else:
            device_type = "unknown"
        firmware = "Switchbot"
        result = {
            "temperature": temp,
            "humidity": humi,
            "battery": batt
        }
    else:
        device_type = "unknown"

    if device_type == "unknown":
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
