# Parser for Brifit BLE advertisements
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def parse_brifit(self, data, source_mac, rssi):
    # check for adstruc length
    msg_length = len(data)
    if msg_length == 21:
        device_id = data[2]
        if device_id == 0x55:
            device_type = "T201"
        else:
            device_type = None
        firmware = "Brifit"

        brifit_mac = data[6:12]
        xvalue = data[12:19]
        (volt, temp, humi, batt) = unpack(">hHHB", xvalue)
        result = {
            "temperature": temp / 100,
            "humidity": humi / 100,
            "voltage": volt / 100,
            "battery": batt
        }
    else:
        device_type = None
    if device_type is None:
        if self.report_unknown == "Brifit":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Brifit DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in message and in service data
    if brifit_mac != source_mac:
        _LOGGER.debug("Invalid MAC address for Brifit device")
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and brifit_mac.lower() not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(brifit_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in brifit_mac[:]),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result


def to_mac(addr: int):
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
