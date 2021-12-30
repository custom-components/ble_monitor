"""Parser for Moat BLE advertisements."""
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)

STATES = {
    0: "unknown",
    1: "initializing",
    2: "idle",
    3: "running",
    4: "charging",
    5: "setup",
    6: "flight menu",
    113: "final test",
    114: "pcb test",
    115: "sleeping",
    116: "transport"
}

MODES = {
    0: "off",
    1: "daily clean",
    2: "sensitive",
    3: "massage",
    4: "whitening",
    5: "deep clean",
    6: "tongue cleaning",
    7: "turbo",
    255: "unknown"
}

SECTORS = {
    1: "sector 1",
    2: "sector 2",
    3: "sector 3",
    4: "sector 4",
    5: "sector 5",
    6: "sector 6",
    7: "sector 7",
    8: "sector 8",
    15: "unknown 1",
    31: "unknown 2",
    23: "unknown 3",
    47: "unknown 4",
    55: "unknown 5",
    254: "last sector",
    255: "no sector"
}


def parse_oral_b(self, data, source_mac, rssi):
    """Parser for Oral-B toothbrush."""
    msg_length = len(data)
    print(data.hex())
    firmware = "Oral-B"
    oral_b_mac = source_mac
    result = {"firmware": firmware}
    if msg_length == 15:
        print(data[7:15].hex())
        device_type = "SmartSeries 7000"
        (state, pressure, counter, mode, sector, sector_timer, no_of_sectors) = unpack(
            ">BBHBBBB", data[7:15]
        )

        if state == 3:
            result.update({"toothbrush": 1})
        else:
            result.update({"toothbrush": 0})

        result.update({
            "toothbrush state": STATES[state],
            "pressure": pressure,
            "counter": counter,
            "mode": MODES[mode],
            "sector": SECTORS[sector],
            "sector timer": sector_timer,
            "number of sectors": no_of_sectors,
        })

    else:
        if self.report_unknown == "Oral-B":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Moat DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in whitelist, if needed
    if self.discovery is False and oral_b_mac.lower() not in self.whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(oral_b_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in oral_b_mac[:]),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result


def to_mac(addr: int):
    """Return formatted MAC address"""
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
