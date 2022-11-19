"""Parser for HHCC BLE advertisements"""
import logging
from struct import unpack

from .const import (
    CONF_MAC,
    CONF_TYPE,
    CONF_PACKET,
    CONF_FIRMWARE,
    CONF_DATA,
    CONF_RSSI,
    CONF_BATTERY,
    CONF_CONDUCTIVITY,
    CONF_ILLUMINANCE,
    CONF_MOISTURE,
    CONF_TEMPERATURE,
)
from .helpers import (
    to_mac,
    to_unformatted_mac,
)

_LOGGER = logging.getLogger(__name__)


def parse_hhcc(self, data: str, source_mac: bytes, rssi: float):
    """HHCC parser"""
    if len(data) == 13:
        device_type = "HHCCJCY10"
        hhcc_mac = source_mac
        xvalue_1 = data[4:7]
        xvalue_2 = data[7:10]
        xvalue_3 = data[10:13]
        packet_id = data[4:13].hex()
        (moist, temp) = unpack(">BH", xvalue_1)
        (illu,) = unpack(">i", b'\x00' + xvalue_2)
        (batt, cond) = unpack(">BH", xvalue_3)
        sensor_data = {
            CONF_TYPE: device_type,
            CONF_PACKET: packet_id,
            CONF_FIRMWARE: "HHCC",
            CONF_DATA: True,
            CONF_TEMPERATURE: temp / 10,
            CONF_MOISTURE: moist,
            CONF_ILLUMINANCE: illu,
            CONF_CONDUCTIVITY: cond,
            CONF_BATTERY: batt,
            CONF_RSSI: rssi,
            CONF_MAC: to_unformatted_mac(hhcc_mac),
        }
    else:
        if self.report_unknown == "HHCC":
            _LOGGER.info(
                "BLE ADV from UNKNOWN HHCC DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # Check for duplicate messages
    if packet_id:
        print("packet_id is", packet_id)
        try:
            prev_packet = self.lpacket_ids[hhcc_mac]
        except KeyError:
            # start with empty first packet
            prev_packet = None
        if prev_packet == packet_id:
            # only process new messages
            if self.filter_duplicates is True:
                return None
        self.lpacket_ids[hhcc_mac] = packet_id
    else:
        packet_id = "no packet id"

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and hhcc_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(hhcc_mac))
        return None

    return sensor_data
