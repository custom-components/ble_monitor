"""Parser for Michelin TMS BLE advertisements."""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)

def parse_michelin_tms(self, data: bytes, mac: bytes):
    """Parser for Michelin TMS."""
    msg_length = len(data)
    firmware = "TMS"
    result = {"firmware": firmware}
    frame_type = data[5]
    device_type = "TMS AL"
    if frame_type == 0x03:
        if msg_length != 14:
                _LOGGER.error("Found %s bytes from sensor: %s", msg_length, to_mac(mac))
                return
        (raw_temp, raw_volt, absolute_pressure_bar, tyre_id, step, frame_counter) = unpack(
            "<BBH3sBL", data[6:18]
        )
        temperature_celcius = raw_temp - 60
        battery_voltage = round((raw_volt / 100) + 1.0, 2)
        result.update({
            "temperature": temperature_celcius,
            "voltage": battery_voltage,
            "pressure": absolute_pressure_bar,
            "count": frame_counter,
            "text": tyre_id,
        })

    else:
        _LOGGER.info(
            "BLE ADV from UNKNOWN TMS DEVICE: MAC: %s, ADV: %s",
            to_mac(mac),
            data.hex()
        )
        return None

    result.update({
        "mac": to_unformatted_mac(mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result
