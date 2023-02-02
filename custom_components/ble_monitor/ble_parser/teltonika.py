"""Parser for Teltonika BLE advertisements"""
import logging
from struct import unpack

from .helpers import (
    to_mac,
    to_unformatted_mac,
)

_LOGGER = logging.getLogger(__name__)


def parse_teltonika(self, data, complete_local_name, source_mac, rssi):
    """Teltonika parser"""
    result = {"firmware": "Teltonika"}
    teltonika_mac = source_mac

    if complete_local_name == "PUCK_T1":
        device_type = "Blue Puck T"
    elif complete_local_name == "PUCK_TH":
        device_type = "Blue Puck RHT"
    elif complete_local_name[0:3] == "C T":
        device_type = "Blue Coin T"
    elif complete_local_name[0:3] == "P T":
        device_type = "Blue Puck T"
    elif complete_local_name[0:5] == "P RHT":
        device_type = "Blue Puck RHT"
    else:
        device_type = None

    # Teltonika adv contain one or two 0x16 service data packets (temperature/humidity)
    packet_start = 0
    data_size = len(data)
    while data_size > 1:
        packet_size = data[packet_start] + 1
        if packet_size > 1 and packet_size <= packet_size:
            packet = data[packet_start:packet_start + packet_size]
            packet_type = packet[1]
            if packet_type == 0x16 and packet_size > 4:
                uuid16 = (packet[3] << 8) | packet[2]
                if uuid16 == 0x2A6E:
                    # Temperature
                    (temp,) = unpack("<h", packet[4:])
                    result.update({"temperature": temp / 100})
                elif uuid16 == 0x2A6F:
                    # Humidity
                    (humi,) = unpack("<B", packet[4:])
                    result.update({"humidity": humi})
            elif packet_type == 0xFF and packet_size > 4:
                comp_id = (packet[3] << 8) | packet[2]
                meas_type = packet[4]

                if comp_id == 0x0757:
                    if meas_type == 0x12:
                        # Temperature
                        (temp,) = unpack("<h", packet[5:7])
                        result.update({"temperature": temp / 100})
                    elif meas_type == 0x21:
                        # Humidity + temperature
                        (humi, _, temp) = unpack("<bbh", packet[5:9])
                        result.update(
                            {"temperature": temp / 100, "humidity": humi}
                        )
                    elif meas_type == 0xF1:
                        # Battery
                        (batt,) = unpack("<b", packet[5:6])
                        result.update({"battery": batt})
        data_size -= packet_size
        packet_start += packet_size

    if device_type is None:
        if self.report_unknown == "Teltonika":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Teltonika DEVICE: RSSI: %s, MAC: %s, DEVICE TYPE: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                device_type,
                data.hex()
            )
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and teltonika_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(teltonika_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": to_unformatted_mac(teltonika_mac),
        "type": device_type,
        "packet": "no packet id",
        "data": True
    })
    return result
