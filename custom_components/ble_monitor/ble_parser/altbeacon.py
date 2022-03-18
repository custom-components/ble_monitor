"""Parser for AltBeacon BLE advertisements"""
import logging
from struct import unpack
from uuid import UUID
from typing import Final

from .const import (
    CONF_MAC,
    CONF_TYPE,
    CONF_PACKET,
    CONF_FIRMWARE,
    CONF_MANUFACTURER,
    CONF_DATA,
    CONF_RSSI,
    CONF_UUID,
    CONF_TRACKER_ID,
    CONF_MAJOR,
    CONF_MINOR,
    CONF_MEASURED_POWER,

    MANUFACTURER_DICT,
    DEFAULT_MANUFACTURER,
)

_LOGGER = logging.getLogger(__name__)

DEVICE_TYPE: Final = "AltBeacon"


def parse_altbeacon(self, data: str, comp_id: int, source_mac: str, rssi: float):
    if len(data) >= 27:
        uuid = data[6:22]
        (major, minor, power) = unpack(">HHb", data[22:27])

        tracker_data = {
            CONF_RSSI: rssi,
            CONF_MAC: to_mac(source_mac),
            CONF_UUID: to_uuid(uuid).replace('-', ''),
            CONF_TRACKER_ID: uuid,
            CONF_MAJOR: major,
            CONF_MINOR: minor,
            CONF_MEASURED_POWER: power,
        }

        sensor_data = {
            CONF_TYPE: DEVICE_TYPE,
            CONF_PACKET: "no packet id",
            CONF_FIRMWARE: DEVICE_TYPE,
            CONF_MANUFACTURER: MANUFACTURER_DICT[comp_id] \
                if comp_id in MANUFACTURER_DICT \
                else DEFAULT_MANUFACTURER,
            CONF_DATA: True
        } | tracker_data
    else:
        if self.report_unknown == DEVICE_TYPE:
            _LOGGER.info(
                "BLE ADV from UNKNOWN %s DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                DEVICE_TYPE,
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


def to_uuid(uuid: str) -> str:
    """Return formatted UUID"""
    return str(UUID(''.join('{:02X}'.format(x) for x in uuid)))


def to_mac(addr: str) -> str:
    """Return formatted MAC address"""
    return ':'.join(f'{i:02X}' for i in addr)
