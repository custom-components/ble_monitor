"""Parser for BLE advertisements used by Passive BLE monitor integration."""
import logging

from .atc import parse_atc
from .kegtron import parse_kegtron
from .miscale import parse_miscale
from .xiaomi import parse_xiaomi
from .qingping import parse_qingping

_LOGGER = logging.getLogger(__name__)


def ble_parser(self, data):
    """Parse the raw data."""

    # check if packet is Extended scan result
    is_ext_packet = True if data[3] == 0x0d else False

    # check for service data of supported manufacturers
    xiaomi_index = data.find(b'\x16\x95\xFE', 15 + 15 if is_ext_packet else 0)
    qingping_index = data.find(b'\x16\xCD\xFD', 15 + 15 if is_ext_packet else 0)
    atc_index = data.find(b'\x16\x1A\x18', 15 + 15 if is_ext_packet else 0)
    miscale_v1_index = data.find(b'\x16\x1D\x18', 15 + 15 if is_ext_packet else 0)
    miscale_v2_index = data.find(b'\x16\x1B\x18', 15 + 15 if is_ext_packet else 0)
    kegtron_index = data.find(b'\x1E\xFF\xFF\xFF', 14 + 15 if is_ext_packet else 0)

    if xiaomi_index != -1:
        return parse_xiaomi(self, data, xiaomi_index, is_ext_packet)
    elif qingping_index != -1:
        return parse_qingping(self, data, qingping_index, is_ext_packet)
    elif atc_index != -1:
        return parse_atc(self, data, atc_index, is_ext_packet)
    elif miscale_v1_index != -1:
        return parse_miscale(self, data, miscale_v1_index, is_ext_packet)
    elif miscale_v2_index != -1:
        return parse_miscale(self, data, miscale_v2_index, is_ext_packet)
    elif kegtron_index != -1:
        return parse_kegtron(self, data, kegtron_index, is_ext_packet)
    elif self.report_unknown == "Other":
        _LOGGER.info("Unknown advertisement received: %s", data.hex())
        return None, None, None
    else:
        return None, None, None
