"""Parser for Relsib EClerk-Eco-RHTC BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_relsib(self, data: bytes, mac: bytes):
    """Relsib parser"""
    msg_length = len(data)
    uuid16 = (data[3] << 8) | data[2]
    result = {
        "packet": "no packet id",
        "mac": to_unformatted_mac(mac),
        "firmware": "Relsib",
    }
    if uuid16 in [0xAA20, 0xAA21, 0xAA22] and msg_length == 26:
        device_type = "EClerk Eco"

        if data[2] == 0x20:
            xdata_point = 8
        else:
            xdata_point = 4

        # Device is sending placeholder when sensor is not ready
        nan = 0x8000

        (temp, humi, co2) = unpack("<HHH", data[xdata_point:xdata_point + 6])
        if temp != nan:
            result.update({"temperature": temp / 100})
        if humi != nan:
            result.update({"humidity": humi / 100})
        if co2 != nan:
            result.update({"co2": co2})

        if data[2] == 0x20:
            # Only 0xAA20 packet has battery info
            battery = data[17]
            # First bit means power adapter plugged in
            if battery & 0b10000000:
                result.update({"battery": 100})
            else:
                result.update({"battery": battery & 0b01111111})
    elif uuid16 in [0x1809] and msg_length == 20:
        device_type = "WH52"
        try:
            temp = round((int.from_bytes(data[4:6], byteorder='big') / 65535) * 175 - 45, 2)
            humi = round((int.from_bytes(data[10:12], byteorder='big') / 65535) * 175 - 45, 2)
            result.update({"temperature": temp, "humidity": humi})
        except ValueError:
            device_type = None
    elif uuid16 in [0x1809] and msg_length == 10:
        device_type = "WT51"
        try:
            temp = (float(data[4:].decode("utf-8")))
            result.update({"temperature": temp})
        except ValueError:
            device_type = None
    else:
        device_type = None
    if device_type is None:
        if self.report_unknown == "Relsib":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Relsib DEVICE: MAC: %s, ADV: %s",
                to_mac(mac),
                data.hex()
            )
        return None

    result.update({
        "type": device_type,
        "data": True
    })
    return result
