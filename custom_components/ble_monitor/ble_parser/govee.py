"""Parser for Govee BLE advertisements"""
import logging
from struct import unpack

from .helpers import (
    to_mac,
    to_unformatted_mac,
)

_LOGGER = logging.getLogger(__name__)


def decode_temps(packet_value: int) -> float:
    """Decode potential negative temperatures."""
    # https://github.com/Thrilleratplay/GoveeWatcher/issues/2
    if packet_value & 0x800000:
        return float((packet_value ^ 0x800000) / -10000)
    return float(packet_value / 10000)


def decode_temps_probes(packet_value: int) -> float:
    """Filter potential negative temperatures."""
    if packet_value < 0:
        return 0.0
    return float(packet_value / 100)


def parse_govee(self, data, source_mac, rssi):
    """Parser for Govee sensors"""
    # The parser needs to handle the bug in the Govee BLE advertisement
    # data as INTELLI_ROCKS sometimes ends up glued on to the end of the message
    if len(data) > 25 and b"INTELLI_ROCKS" in data:
        data = data[:-25]
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
        device_type = "H5051/H5071"
        (temp, humi, batt) = unpack("<hHB", data[5:10])
        result.update({"temperature": temp / 100, "humidity": humi / 100, "battery": batt})
    elif msg_length == 13 and device_id == 0x0001:
        packet_5178 = data[7:10].hex()
        packet = int(packet_5178, 16)
        temp = decode_temps(packet)
        humi = float((packet % 1000) / 10)
        batt = int(data[10])
        sensor_id = data[6]
        result.update(
            {
                "temperature": temp,
                "humidity": humi,
                "battery": batt,
                "sensor id": sensor_id
            }
        )
        if sensor_id == 0:
            device_type = "H5178"
        elif sensor_id == 1:
            device_type = "H5178-outdoor"
            govee_mac_outdoor = int.from_bytes(govee_mac, 'big') + 1
            govee_mac = bytearray(govee_mac_outdoor.to_bytes(len(govee_mac), 'big'))
        else:
            _LOGGER.debug(
                "Unknown sensor id for Govee H5178, please report to the developers, data: %s",
                data.hex()
            )
    elif msg_length == 13 and device_id == 0x8801:
        device_type = "H5179"
        (temp, humi, batt) = unpack("<hHB", data[8:13])
        result.update({"temperature": temp / 100, "humidity": humi / 100, "battery": batt})
    elif msg_length == 18:
        device_type = "H5183"
        (temp_probe_1, temp_alarm_1) = unpack(">hh", data[12:16])
        result.update({
            "temperature probe 1": decode_temps_probes(temp_probe_1),
            "temperature alarm probe 1": decode_temps_probes(temp_alarm_1)
        })
    elif msg_length == 21:
        device_type = "H5182"
        (temp_probe_1, temp_alarm_1, dummy, temp_probe_2, temp_alarm_2) = unpack(">hhbhh", data[12:21])
        result.update({
            "temperature probe 1": decode_temps_probes(temp_probe_1),
            "temperature alarm probe 1": decode_temps_probes(temp_alarm_1),
            "temperature probe 2": decode_temps_probes(temp_probe_2),
            "temperature alarm probe 2": decode_temps_probes(temp_alarm_2)
        })
    elif msg_length == 24:
        device_type = "H5185"
        (temp_probe_1, temp_alarm_1, dummy, temp_probe_2, temp_alarm_2) = unpack(">hhhhh", data[12:22])
        result.update({
            "temperature probe 1": decode_temps_probes(temp_probe_1),
            "temperature alarm probe 1": decode_temps_probes(temp_alarm_1),
            "temperature probe 2": decode_temps_probes(temp_probe_2),
            "temperature alarm probe 2": decode_temps_probes(temp_alarm_2)
        })
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
        "mac": to_unformatted_mac(govee_mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result
