"""Parser for Eddystone-TLM BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)

TLM_FRAME_TYPE = 0x20
TLM_VERSION = 0x00
TLM_TEMPERATURE_UNSUPPORTED = -128.0


def parse_eddystone_tlm(self, data: bytes, mac: bytes):
    """Parser for Eddystone-TLM beacons"""
    device_type = "Eddystone-TLM"
    result = {
        "mac": to_unformatted_mac(mac),
        "type": device_type,
        "data": False,
    }
    (frame_type, version, volt, temp_int, temp_frac, adv_cnt) = unpack(
        ">BBHbBI", data[4:14]
    )
    if frame_type != TLM_FRAME_TYPE or version != TLM_VERSION:
        result = None
    else:
        result.update(
            {
                "packet": adv_cnt,
                "data": True,
            }
        )
        # a voltage of 0 means the beacon does not report its battery level
        if volt != 0:
            result["voltage"] = volt / 1000
        temperature = temp_int + temp_frac / 256
        if temperature != TLM_TEMPERATURE_UNSUPPORTED:
            result["temperature"] = round(temperature, 2)
    if result is None:
        if self.report_unknown == "Eddystone":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Eddystone DEVICE: MAC: %s, ADV: %s",
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
