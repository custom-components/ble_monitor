"""Parser for Laica Smart Scale BLE advertisements"""
import logging

from .helpers import to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def decrypt_value(arr):
    """Decrypt data"""
    hex_string = ''
    for x in arr:
        hex_string += '%02x' % (x ^ 0xa0)
    return int(hex_string, 16)


def read_weight(data):
    """Parse weight"""
    val = decrypt_value(data[10:14])
    weight = round((val & 0x3ffff) / 100) / 10

    return weight


def read_impedance(data):
    """Parse impedance"""
    impedance = decrypt_value(data[10:12])
    impedance = min(max(impedance, 430), 630)

    return impedance


def parse_laica(self, data: bytes, mac: bytes):
    """Parser for Laica sensors"""
    xvalue = data[4:]

    result = {
        "type": "Laica Smart Scale",
        "firmware": "Laica",
        "mac": to_unformatted_mac(mac),
        "data": False,
    }

    if data[14] == 0x06:
        impedance = read_impedance(data)
        result.update({
            "impedance": impedance,
            "data": True,
        })
    elif data[14] == 0x0D:
        weight = read_weight(data)
        result.update({
            "weight": weight,
            "data": True,
        })

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

    result.update({
        "packet": packet_id,
    })

    return result
