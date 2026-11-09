"""Parser for Thermosafer BLE advertisements."""

from .helpers import to_unformatted_mac


def parse_thermosafer(self, data: bytes, mac: bytes):
    """Parse a Thermosafer advertisement."""
    # AD structure: length, type, company ID (0xBC0E), 20-byte payload.
    if len(data) != 24 or data[0] != 0x17 or data[4] != 0x01:
        return None

    battery = data[10]
    temperature = int.from_bytes(data[11:13], byteorder="big", signed=True) / 100

    if battery > 100:
        return None

    return {
        "temperature": temperature,
        "battery": battery,
        "mac": to_unformatted_mac(mac),
        "type": "Thermosafer",
        "packet": "no packet id",
        "firmware": "Thermosafer",
        "data": True,
    }
