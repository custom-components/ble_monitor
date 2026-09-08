"""Parser for Almendo bluSensor BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_almendo(self, data: bytes, mac: bytes):
    """Almendo parser"""
    result = {
        "mac": to_unformatted_mac(mac),
        "data": False,
        "packet": "no packet id"
    }
    adstruct_type = data[1]
    if adstruct_type == 0xFF:
        comp_id = (data[3] << 8) | data[2]
        if comp_id == 0x06E8:
            if len(data) < 10:
                result = None
            elif data[4] == 1 and data[6] == 0x0A and len(data) < 20:
                result = None
            elif data[4] == 1 and data[6] == 0x0A:
                # version, device_type, device_model, hw_revistion,
                # status_bits, sstatus_code
                version, _, dmodel, _, _, _ = data[4:10]
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
                "BLE ADV from UNKNOWN Almendo DEVICE: "
                "MAC: %s, ADV: %s",
                to_mac(mac),
                data.hex(),
            )
        return None

    if version != 1:
        _LOGGER.info(
            "Protocol version %i on device %s not yet known "
            "by the Almendo parser",
            version,
            to_mac(mac),
        )
    return result
