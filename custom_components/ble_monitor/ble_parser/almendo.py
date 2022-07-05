"""Parser for Almendo bluSensor BLE advertisements"""
import logging
from struct import unpack
from .helpers import (
    to_mac,
    to_unformatted_mac,
)

_LOGGER = logging.getLogger(__name__)


def parse_almendo(self, data, source_mac, rssi):
    """Almendo parser"""
    result = {
        "mac": to_unformatted_mac(source_mac),
        "rssi": rssi,
        "data": False,
        "packet": "no packet id"
    }
    adstruct_type = data[1]
    if adstruct_type == 0xFF:
        comp_id = (data[3] << 8) | data[2]
        if comp_id == 0x06E8:
            # version, device_type, device_model, hw_revistion,
            # status_bits, sstatus_code
            version, _, dmodel, _, _, _ = data[4:10]
            if version == 1 and dmodel == 0x0A:
                # Almendo bluSensor V1 format (BSP02AIQ)
                # sensor_state, temp, humi, co2e, tvoc, aiq
                (_, temp, humi, co2e, tvoc, aqi) = unpack(
                    "<BhHHHB", data[10:20]
                )

                result.update(
                    {
                        "temperature": round(temp / 100, 2),
                        "humidity": round(humi / 100, 2),
                        "co2": co2e,
                        "tvoc": tvoc,
                        "aqi": aqi,
                        "firmware": "Almendo V1",
                        "type": "bluSensor Mini",
                        "data": True,
                    }
                )
            else:
                result = None
    else:
        result = None
    if result is None:
        if self.report_unknown == "Almendo":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Almendo DEVICE: RSSI: %s, "
                "MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex(),
            )
        return None
    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and source_mac not in self.sensor_whitelist:
        _LOGGER.debug(
            "Discovery is disabled. MAC: %s is not whitelisted!",
            to_mac(source_mac),
        )
        return None
    if version != 1:
        _LOGGER.info(
            "Protocol version %i on device %s not yet known "
            "by the Almendo parser",
            version,
            to_mac(source_mac),
        )
    return result
