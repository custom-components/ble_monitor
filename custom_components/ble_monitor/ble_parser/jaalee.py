"""Parser for Jaalee BLE advertisements"""
import logging
from struct import unpack

from .const import (
    CONF_MAC,
    CONF_TYPE,
    CONF_PACKET,
    CONF_FIRMWARE,
    CONF_DATA,
    CONF_RSSI,
    CONF_UUID,
    CONF_TRACKER_ID,
    CONF_MAJOR,
    CONF_MINOR,
    CONF_MEASURED_POWER,
)
from .helpers import (
    to_mac,
    to_uuid,
    to_unformatted_mac,
)

_LOGGER = logging.getLogger(__name__)


def parse_jaalee(self, data, ibeacon_data, source_mac, rssi):
    """Jaalee parser"""
    msg_length = len(data)
    if msg_length == 15:
        # iBeacon data
        uuid = ibeacon_data[6:22]
        (major, minor, power) = unpack(">HHb", ibeacon_data[22:27])

        tracker_data = {
            CONF_RSSI: rssi,
            CONF_MAC: to_unformatted_mac(source_mac),
            CONF_UUID: to_uuid(uuid).replace('-', ''),
            CONF_TRACKER_ID: uuid,
            CONF_MAJOR: major,
            CONF_MINOR: minor,
            CONF_MEASURED_POWER: power,
        }

        # Jaalee service data
        batt = data[4]
        (temp, humi) = unpack(">HH", data[11:])
        # data follows the iBeacon temperature and humidity definition
        temp = round(175.72 * temp / 65536 - 46.85, 2)
        humi = round(125.0 * humi / 65536 - 6, 2)
        sensor_data = {
            CONF_TYPE: "JHT",
            CONF_PACKET: "no packet id",
            CONF_FIRMWARE: "Jaalee",
            CONF_DATA: True,
            "temperature": temp,
            "humidity": humi,
            "battery": batt
        } | tracker_data
    else:
        if self.report_unknown == "Jaalee":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Jaalee DEVICE: RSSI: %s, MAC: %s, ADV: %s",
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
