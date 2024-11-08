"""Parser for Senssun Scale BLE advertisements"""

import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def read_stable(ctr1):
    """Parse Stable"""
    return int((ctr1 & 0xA0) == 0xA0)

def parse_senssun(self, data: bytes, mac: bytes):
    """Parser for Senssun Scales."""
    xvalue = data[13:19]

    (division, weight, impedance, ctr1) = unpack(">bhhb", xvalue)
    result = {
        "type": "Senssun Smart Scale",
        "firmware": "Senssun",
        "mac": to_unformatted_mac(mac),
        "data": True,
        "impedance": impedance,
        "weight": weight / 100.0,
        "stabilized": read_stable(ctr1),
    }

    # Check for duplicate messages
    packet_id = xvalue.hex()
    try:
        prev_packet = self.lpacket_ids[mac]
    except KeyError:
        # start with empty first packet
        prev_packet = None
    if prev_packet == packet_id:
        # only process new messages
        if self.filter_duplicates is True:
            return None
    self.lpacket_ids[mac] = packet_id
    if prev_packet is None:
        if self.filter_duplicates is True:
            # ignore first message after a restart
            return None

    result.update({
            "packet": packet_id,
    })
    return result
