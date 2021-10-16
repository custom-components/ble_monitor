"""Parser for BlueMaestro BLE advertisements."""
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def parse_bluemaestro(self, data, source_mac, rssi):
    """Parse BlueMaestro advertisement."""
    msg_length = len(data)
    firmware = "BlueMaestro"
    device_id = data[4]
    bluemaestro_mac = source_mac
    msg = data[5:]
    if msg_length == 18 and device_id == 0x17:
        # BlueMaestro Tempo Disc THD
        device_type = "Tempo Disc THD"
        # pylint: disable=unused-variable
        (batt, time_interval, log_cnt, temp, humi, dew_point, mode) = unpack("!BhhhHhH", msg)
        result = {
            "temperature": temp / 10,
            "humidity": humi / 10,
            "battery": batt,
            "dewpoint": dew_point / 10
        }
    elif msg_length == 18 and device_id == 0x1b:
        # BlueMaestro Tempo Disc THPD (sends P instead of D, no D is send)
        device_type = "Tempo Disc THPD"
        # pylint: disable=unused-variable
        (batt, time_interval, log_cnt, temp, humi, press, mode) = unpack("!BhhhHhH", msg)
        result = {
            "temperature": temp / 10,
            "humidity": humi / 10,
            "battery": batt,
            "pressure": press / 10
        }
    else:
        if self.report_unknown == "BlueMaestro":
            _LOGGER.info(
                "BLE ADV from UNKNOWN BlueMaestro DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in whitelist, if needed
    if self.discovery is False and bluemaestro_mac.lower() not in self.whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(bluemaestro_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in bluemaestro_mac[:]),
        "type": device_type,
        "packet": log_cnt,
        "firmware": firmware,
        "data": True
    })
    return result


def to_mac(addr: int):
    """Convert MAC address."""
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
