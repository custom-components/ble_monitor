# Parser for Govee BLE advertisements
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def decode_temps(packet_value: int) -> float:
    """Decode potential negative temperatures."""
    # https://github.com/Thrilleratplay/GoveeWatcher/issues/2
    if packet_value & 0x800000:
        return float((packet_value ^ 0x800000) / -100)
    return float(packet_value / 10000)


def parse_govee(self, data, source_mac, rssi):
    # check for adstruc length
    msg_length = len(data)
    firmware = "Govee"
    govee_mac = source_mac
    device_id = (data[3] << 8) | data[2]
    result = {"firmware": firmware}
    if msg_length == 10 and device_id == 0xEC88:
        device_type = "H5072/H5075"
        packet_5072_5075 = data[5:8].hex()
        packet = int(packet_5072_5075, 16)
        temp = decode_temps(packet)
        humi = float((packet % 1000) / 10)
        batt = int(data[8])
        result.update({"temperature": temp, "humidity": humi, "battery": batt})
    elif msg_length == 10 and device_id == 0x0001:
        device_type = "H5101/H5102/H5177"
        packet_5101_5102 = data[6:9].hex()
        packet = int(packet_5101_5102, 16)
        temp = decode_temps(packet)
        humi = float((packet % 1000) / 10)
        batt = int(data[9])
        result.update({"temperature": temp, "humidity": humi, "battery": batt})
    elif msg_length == 11 and device_id == 0xEC88:
        device_type = "H5074"
        (temp, humi, batt) = unpack("<hHB", data[5:10])
        result.update({"temperature": temp / 100, "humidity": humi / 100, "battery": batt})
    elif msg_length == 13 and device_id == 0xEC88:
        device_type = "H5051"
        (temp, humi, batt) = unpack("<hHB", data[5:10])
        result.update({"temperature": temp / 100, "humidity": humi / 100, "battery": batt})
    elif msg_length == 13 and device_id == 0x0001:
        device_type = "H5178"
        packet_5178 = data[7:10].hex()
        packet = int(packet_5178, 16)
        temp = decode_temps(packet)
        humi = float((packet % 1000) / 10)
        batt = int(data[10])
        sensor_id = data[6]
        if sensor_id == 0:
            result.update(
                {
                    "temperature": temp,
                    "humidity": humi,
                    "battery": batt,
                    "sensor id": sensor_id
                }
            )
        elif sensor_id == 1:
            result.update(
                {
                    "temperature outdoor": temp,
                    "humidity outdoor": humi,
                    "battery": batt,
                    "sensor id": sensor_id
                }
            )
        else:
            _LOGGER.debug("Unknown sensor id for Govee H5178, please report to the developers, data: %s", data.hex())
    elif msg_length == 13 and device_id == 0x8801:
        device_type = "H5179"
        (temp, humi, batt) = unpack("<hHB", data[8:13])
        result.update({"temperature": temp / 100, "humidity": humi / 100, "battery": batt})
    else:
        if self.report_unknown == "Govee":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Govee DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and govee_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(govee_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in govee_mac[:]),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result


def to_mac(addr: int):
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
