"""Parser for Acconeer BLE advertisements"""
import logging
from struct import unpack

from .helpers import (
    to_mac,
    to_unformatted_mac,
)

_LOGGER = logging.getLogger(__name__)

ACCONEER_SENSOR_IDS = {
    0x80: "Acconeer XM122"
}

MEASUREMENTS = {
    0x80: ["presence", "temperature"],
}


def parse_acconeer(self, data, source_mac, rssi):
    """Acconeer parser"""
    msg_length = len(data)
    firmware = "Acconeer"
    acconeer_mac = source_mac
    device_id = data[4]
    xvalue = data[5:]
    result = {"firmware": firmware}

    if msg_length == 19 and device_id in ACCONEER_SENSOR_IDS:
        # Acconeer Sensors
        device_type = ACCONEER_SENSOR_IDS[device_id]
        measurements = MEASUREMENTS[device_id]
        (
            battery_level,
            temperature,
            presence,
            reserved2
        ) = unpack("<HhHQ", xvalue)

        if "presence" in measurements:
            result.update({
                "motion": 0 if presence == 0 else 1,
            })

        if "temperature" in measurements:
            result.update({
                "temperature": temperature,
            })

        result.update({
            "battery": battery_level,
        })
    else:
        device_type = None

    if device_type is None:
        if self.report_unknown == "Acconeer":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Acconeer DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # Check for duplicate messages
    packet_id = xvalue.hex()
    try:
        prev_packet = self.lpacket_ids[acconeer_mac]
    except KeyError:
        # start with empty first packet
        prev_packet = None
    if prev_packet == packet_id:
        # only process new messages
        if self.filter_duplicates is True:
            return None
    self.lpacket_ids[acconeer_mac] = packet_id

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and acconeer_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(acconeer_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": to_unformatted_mac(acconeer_mac),
        "type": device_type,
        "packet": packet_id,
        "firmware": firmware,
        "data": True
    })
    return result
