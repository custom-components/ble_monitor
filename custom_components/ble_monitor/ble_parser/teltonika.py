"""Parser for Teltonika BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_teltonika(self, data: bytes, complete_local_name: str, mac: bytes):
    """Teltonika parser"""
    result = {"firmware": "Teltonika"}
    device_id = (data[3] << 8) | data[2]

    if device_id == 0x089A:
        device_type = "EYE sensor"
    elif complete_local_name == "PUCK_T1":
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
        if packet_size > 1 and packet_size <= data_size:
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
                elif comp_id == 0x089A:
                    flags = packet[5]
                    sensor_data = packet[6:]
                    if flags & (1 << 0):  # bit 0
                        # Temperature
                        (temp,) = unpack(">h", sensor_data[0:2])
                        result.update({"temperature": temp / 100})
                        sensor_data = sensor_data[2:]
                    if flags & (1 << 1):  # bit 1
                        # Humidity
                        humi = sensor_data[0]
                        result.update({"humidity": humi})
                        sensor_data = sensor_data[1:]
                    if flags & (1 << 2):  # bit 2
                        # Magnetic sensor presence
                        if flags & (1 << 3):  # bit 3
                            # magnetic field is detected
                            result.update({"magnetic field detected": 1})
                        else:
                            # magnetic field is not detected
                            result.update({"magnetic field detected": 0})
                    if flags & (1 << 4):  # bit 4
                        # Movement sensor counter
                        # Most significant bit indicates movement state
                        # 15 least significant bits represent count of movement events.
                        moving = sensor_data[0] & (1 << 7)
                        count = ((sensor_data[0] & 0b01111111) << 8) + sensor_data[1]
                        result.update({"moving": moving, "movement counter": count})
                        sensor_data = sensor_data[2:]
                    if flags & (1 << 5):  # bit 5
                        # Movement sensor angle
                        # Most significant byte – pitch (-90/+90)
                        # Two least significant bytes – roll (-180/+180)
                        (pitch, roll,) = unpack(">bh", sensor_data[0:3])
                        result.update({"roll": roll, "pitch": pitch})
                        sensor_data = sensor_data[3:]
                    if flags & (1 << 6):  # bit 6
                        # Low battery indication sensor presence
                        result.update({"battery low": 1})
                    if flags & (1 << 7):  # bit 7
                        # Battery voltage value presence
                        volt = round(2.0 + sensor_data[0] * 0.01, 3)
                        result.update({"voltage": volt})
        data_size -= packet_size
        packet_start += packet_size

    if device_type is None:
        if self.report_unknown == "Teltonika":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Teltonika DEVICE: MAC: %s, DEVICE TYPE: %s, ADV: %s",
                to_mac(mac),
                device_type,
                data.hex()
            )
        return None

    result.update({
        "mac": to_unformatted_mac(mac),
        "type": device_type,
        "packet": "no packet id",
        "data": True
    })
    return result
