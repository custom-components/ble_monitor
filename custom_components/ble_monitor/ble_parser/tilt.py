"""Parser for Tilt BLE advertisements"""
import logging
from struct import unpack

from .const import (CONF_DATA, CONF_FIRMWARE, CONF_GRAVITY, CONF_MAC,
                    CONF_MAJOR, CONF_MEASURED_POWER, CONF_MINOR, CONF_PACKET,
                    CONF_RSSI, CONF_TEMPERATURE, CONF_TRACKER_ID, CONF_TYPE,
                    CONF_UUID, TILT_TYPES)
from .helpers import to_mac, to_unformatted_mac, to_uuid

_LOGGER = logging.getLogger(__name__)


def parse_tilt(self, data: str, source_mac: str, rssi: float):
    """Tilt parser"""
    if data[5] == 0x15 and len(data) == 27:
        uuid = data[6:22]
        color = TILT_TYPES[int.from_bytes(uuid, byteorder='big')]
        device_type = "Tilt " + color
        (major, minor, power) = unpack(">hhb", data[22:27])

        tracker_data = {
            CONF_RSSI: rssi,
            CONF_MAC: to_unformatted_mac(source_mac),
            CONF_UUID: to_uuid(uuid).replace('-', ''),
            CONF_TRACKER_ID: uuid,
            CONF_MAJOR: major,
            CONF_MINOR: minor,
            CONF_MEASURED_POWER: power,
        }

        sensor_data = {
            CONF_TYPE: device_type,
            CONF_PACKET: "no packet id",
            CONF_FIRMWARE: "Tilt",
            CONF_DATA: True,
            CONF_TEMPERATURE: (major - 32) * 5 / 9,
            CONF_GRAVITY: minor / 1000,
        } | tracker_data
    else:
        if self.report_unknown == "Tilt":
            _LOGGER.info(
                "BLE ADV from UNKNOWN TILT DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None, None

    # check for UUID presence in sensor whitelist, if needed
    if self.discovery is False and uuid and uuid not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. UUID: %s is not whitelisted!", to_uuid(uuid))

        return None, None

    return sensor_data, tracker_data
