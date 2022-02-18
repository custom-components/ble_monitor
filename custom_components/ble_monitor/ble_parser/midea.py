# Parser for Midea BLE advertisements
import logging

_LOGGER = logging.getLogger(__name__)


def parse_midea(self, data, source_mac, rssi):
    """Parser for midea sensors"""
    if self.report_unknown == "Midea":
        _LOGGER.info(
            "BLE ADV from UNKNOWN Midea DEVICE: RSSI: %s, MAC: %s, ADV: %s",
            rssi,
            to_mac(source_mac),
            data.hex()
        )
    return None


def to_mac(addr: int):
    """Return formatted MAC address"""
    return ':'.join(f'{i:02X}' for i in addr)
