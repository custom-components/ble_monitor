"""Parser for Air Mentor BLE advertisements"""
import logging
from struct import unpack
import math

from .helpers import (
    to_mac,
    to_unformatted_mac,
)

_LOGGER = logging.getLogger(__name__)


def aqi_to_air_quality(aqi):
    if aqi <= 50:
        return "good"
    elif aqi <= 100:
        return "moderate"
    elif aqi <= 150:
        return "unhealthy for sensitive people"
    elif aqi <= 200:
        return "unhealthy"
    elif aqi <= 250:
        return "very unhealthy"
    else:
        return "hazardous"


def tvoc_ppb_to_ugm3(tvoc_ppb):
    """Convert TVOC from ppb to ug/m^3.

    ref: https://www.catsensors.com/media/pdf/Sensor_Sensirion_IAM.pdf
    """
    M_gas = 110
    V_m = 0.0244 * 1000
    tvoc_ugm3 = float(tvoc_ppb) * M_gas / V_m
    return tvoc_ugm3


def parse_pro2(msg_type, xvalue):
    if msg_type in [0x12, 0x22]:
        (tvoc_ppb, temp, temp_cal, humi, aqi) = unpack(">HHBBH", xvalue)
        tvoc_ugm3 = tvoc_ppb_to_ugm3(tvoc_ppb)
        temperature = (temp - 4000) * 0.01
        temperature_calibrated = temperature - temp_cal * 0.1
        humi = round(
            humi * math.exp(temperature * 17.62 / (temperature + 243.12)) / math.exp(
                temperature_calibrated * 17.62 / (temperature_calibrated + 243.12)
            ), 2
        )
        air_quality = aqi_to_air_quality(aqi)
        return {
            "tvoc": round(tvoc_ugm3, 2),
            "temperature": round(temperature, 2),
            "temperature calibrated": round(temperature_calibrated, 2),
            "humidity": round(humi, 2),
            "aqi": aqi,
            "air quality": air_quality
        }
    elif msg_type in [0x11, 0x21]:
        (co2, pm25, pm10, co, o3) = unpack(">HHHBB", xvalue)
        # CO and O3 are not used
        return {
            "co2": co2,
            "pm2.5": pm25,
            "pm10": pm10,
        }
    else:
        return None


def parse_2s(msg_type, xvalue):
    if msg_type in [0x12, 0x22]:
        # 4 unknown bytes at the end.
        (tvoc_ppb, temp, temp_cal, humi, aqi, _, _) = unpack(">HHBBHHH", xvalue)

        tvoc_ugm3 = tvoc_ppb_to_ugm3(tvoc_ppb)
        temperature = (temp - 4000) * 0.01
        temperature_calibrated = temperature - temp_cal * 0.1

        # No calibration for humidity. Use the raw value. It is aligned what observe in iOS app.

        air_quality = aqi_to_air_quality(aqi)

        return {
            "tvoc": round(tvoc_ugm3, 2),
            "temperature": round(temperature, 2),
            "temperature calibrated": round(temperature_calibrated, 2),
            "humidity": round(humi, 2),
            "aqi": aqi,
            "air quality": air_quality
        }
    elif msg_type in [0x11, 0x21]:
        (co2, pm25, pm10, _, hcho_ppb, _) = unpack(">HHHHHH", xvalue)

        # formaldehyde: At 25 °C, 1 ppm = 1.228 mg/m3 and 1 mg/m3 = 0.814 ppm.
        M_hcho = 1.228
        hcho_mgm3 = hcho_ppb * 0.001 * M_hcho

        return {
            "co2": co2,
            "pm2.5": pm25,
            "pm10": pm10,
            "formaldehyde": round(hcho_mgm3, 6)
        }
    else:
        return None


def parse_airmentor(self, data: bytes, source_mac: str, rssi):
    """Parser for Air Mentor"""
    data_length = len(data)
    airmentor_mac = source_mac

    device_type = None
    result = None
    if data_length == 12:
        msg_type = data[2]
        xvalue = data[4:]
        device_type = "Air Mentor Pro 2"
        firmware = "Air Mentor"
        result = parse_pro2(msg_type, xvalue)
    elif data_length == 16:
        msg_type = data[2]
        xvalue = data[4:]
        device_type = "Air Mentor 2S"
        firmware = "Air Mentor"
        result = parse_2s(msg_type, xvalue)

    if device_type is None or result is None:
        if self.report_unknown == "Air Mentor":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Air Mentor DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and airmentor_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(airmentor_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": to_unformatted_mac(airmentor_mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result
