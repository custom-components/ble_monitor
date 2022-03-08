"""Parser for Air Mentor BLE advertisements"""
import logging
from struct import unpack
import math

_LOGGER = logging.getLogger(__name__)


def parse_airmentor(self, data, source_mac, rssi):
    """Parser for Air Mentor"""
    data_length = len(data)
    if data_length == 12:
        device_type = "Air Mentor Pro 2"
        firmware = "Air Mentor"
        airmentor_mac = source_mac
        msg_type = data[2]
        xvalue = data[4:]
        if msg_type == 0x22:
            (tvoc, temp, temp_cal, humi, iaq) = unpack(">HHBBH", xvalue)
            temperature = (temp - 4000) * 0.01
            temperature_calibrated = temperature - temp_cal * 0.1
            humi = round(float(int("0x2d", 16)) * math.exp(temperature * 17.62 / (temperature + 243.12)) / math.exp(
                temperature_calibrated * 17.62 / (temperature_calibrated + 243.12)), 2
            )
            result = {
                "tvoc": tvoc,
                "temperature": round(temperature, 2),
                "temperature calibrated": round(temperature_calibrated, 2),
                "humidity": round(humi, 2),
                "iaq": iaq
            }
        if msg_type == 0x21:
            (co2, pm25, pm10, battery, voltage) = unpack(">HHHBB", xvalue)
            # Battery and voltage sensors are for testing only. They probably mean something else [CO O3].
            result = {
                "co2": co2,
                "pm2.5": pm25,
                "pm10": pm10,
                "battery": battery,
                "voltage": voltage,
            }
    else:
        device_type = None
    if device_type is None:
        if self.report_unknown == "Air Mentor":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Air Mentor DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and airmentor_mac.lower() not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(airmentor_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join(f'{i:02X}' for i in airmentor_mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result


def to_mac(addr: int):
    """Return formatted MAC address"""
    return ':'.join(f'{i:02X}' for i in addr)
