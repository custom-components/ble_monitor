"""Parser for KKM beacon BLE advertisements"""
import logging
import math
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_kkm(self, data: bytes, mac: str):
    """Parser for KKM sensors."""
    device_type = "K6 Sensor Beacon"
    result = {
        "mac": to_unformatted_mac(mac),
        "type": device_type,
        "data": False,
    }
    if len(data) == 19:
        # K6 Sensor Beacon
        (frame_type, version, control_byte, volt, temp, temp_frac, humi, humi_frac, accx, accy, accz) = unpack(
            ">BBBHbBBBhhh", data[4:19]
        )
        if frame_type == 0x21 and version == 1:
            if temp < 0:
                temperature = -(temp + 128 + temp_frac / 100)
            else:
                temperature = temp + temp_frac / 100
            humidity = humi + humi_frac / 100
            result.update(
                {
                    "temperature": temperature,
                    "humidity": humidity,
                    "acceleration": round(math.sqrt(accx ** 2 + accy ** 2 + accz ** 2), 1),
                    "acceleration x": accx,
                    "acceleration y": accy,
                    "acceleration z": accz,
                    "voltage": volt / 1000,
                    "firmware": "KKM",
                    "packet": "no packet id",
                    "data": True,
                }
            )
        else:
            result = None
    else:
        result = None
    if result is None:
        if self.report_unknown == "KKM":
            _LOGGER.info(
                "BLE ADV from UNKNOWN KKM DEVICE: MAC: %s, ADV: %s",
                to_mac(mac),
                data.hex(),
            )
        return None
    # reformat battery info to match BLE monitor format
    if "voltage" in result:
        voltage = result["voltage"]
        # calculate battery in %
        if voltage >= 3.00:
            batt = 100
        elif voltage >= 2.60:
            batt = 60 + (voltage - 2.60) * 100
        elif voltage >= 2.50:
            batt = 40 + (voltage - 2.50) * 200
        elif voltage >= 2.45:
            batt = 20 + (voltage - 2.45) * 400
        else:
            batt = 0
        result["battery"] = round(batt, 1)

    return result
