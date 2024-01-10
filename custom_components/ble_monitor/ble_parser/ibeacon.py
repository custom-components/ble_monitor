"""Parser for iBeacon BLE advertisements"""
import logging
from struct import unpack
from typing import Final

from .const import (CONF_CYPRESS_HUMIDITY, CONF_CYPRESS_TEMPERATURE, CONF_DATA,
                    CONF_FIRMWARE, CONF_MAC, CONF_MAJOR, CONF_MEASURED_POWER,
                    CONF_MINOR, CONF_PACKET, CONF_TRACKER_ID, CONF_TYPE,
                    CONF_UUID)
from .helpers import to_mac, to_unformatted_mac, to_uuid

_LOGGER = logging.getLogger(__name__)

DEVICE_TYPE: Final = "iBeacon"


def parse_ibeacon(self, data: str, mac: str):
    """Parse iBeacon advertisements"""
    if data[5] == 0x15 and len(data) >= 27:
        uuid = data[6:22]
        (major, minor, power) = unpack(">HHb", data[22:27])

        tracker_data = {
            CONF_MAC: to_unformatted_mac(mac),
            CONF_UUID: to_uuid(uuid).replace('-', ''),
            CONF_TRACKER_ID: uuid,
            CONF_MAJOR: major,
            CONF_MINOR: minor,
            CONF_MEASURED_POWER: power,
            CONF_CYPRESS_TEMPERATURE: 175.72 * ((minor & 0xff) * 256) / 65536 - 46.85,
            CONF_CYPRESS_HUMIDITY: 125.0 * (minor & 0xff00) / 65536 - 6,
        }

        sensor_data = {
            CONF_TYPE: DEVICE_TYPE,
            CONF_PACKET: "no packet id",
            CONF_FIRMWARE: DEVICE_TYPE,
            CONF_DATA: True
        } | tracker_data
    else:
        if self.report_unknown == DEVICE_TYPE:
            _LOGGER.info(
                "BLE ADV from UNKNOWN %s DEVICE: MAC: %s, ADV: %s",
                DEVICE_TYPE,
                to_mac(mac),
                data.hex()
            )
        return None, None

    return sensor_data, tracker_data
