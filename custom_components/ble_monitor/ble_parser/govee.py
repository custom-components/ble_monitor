# Parser for Govee BLE advertisements
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def parse_govee(self, data, source_mac, rssi):
    # check for adstruc length
    msg_length = len(data)
    firmware = "Govee"
    govee_mac = source_mac
    device_id = (data[3] << 8) | data[2]
    result = {"firmware": firmware}
    if msg_length == 11 and device_id == 0xEC88:
        device_type = "H5074"
        (temp, humi, batt) = unpack("<hHB", data[5:10])
        result.update({"temperature": temp / 100, "humidity": humi / 100, "battery": batt})
    # Other govee devices to be added here
    else:
        if self.report_unknown == "Govee":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Govee DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in whitelist, if needed
    if self.discovery is False and govee_mac.lower() not in self.whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(govee_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in govee_mac[:]),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result


def to_mac(addr: int):
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
