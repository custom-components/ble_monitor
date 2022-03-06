"""Parser for Relsib EClerk-Eco-RHTC BLE advertisements"""
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def parse_relsib(self, data, source_mac, rssi):
    """Relsib parser"""
    msg_length = len(data)
    if msg_length == 26:
        firmware = "Relsib (EClerk Eco v9a)"
        device_type = "EClerk Eco"
        relsib_mac = source_mac

        result = {
            "rssi": rssi,
            "packet": "no packet id",
        }
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

    else:
        device_type = None
    if device_type is None:
        if self.report_unknown == "Relsib":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Relsib DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and relsib_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(relsib_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in relsib_mac[:]),
        "type": device_type,
        "firmware": firmware,
        "data": True
    })
    return result


def to_mac(addr: int):
    """Return formatted MAC address"""
    return ':'.join(f'{i:02X}' for i in addr)
