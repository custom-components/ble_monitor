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


def parse_oral_b(self, data, source_mac, rssi):
    """Parser for Oral-B toothbrush."""
    msg_length = len(data)
    firmware = "Oral-B"
    oral_b_mac = source_mac
    result = {"firmware": firmware}
    if msg_length == 15:
        device_type = "SmartSeries 7000"
        (state, pressure, counter, mode, sector, sector_timer, no_of_sectors) = unpack(
            ">BBHBBBB", data[7:15]
        )

        if state == 3:
            result.update({"toothbrush": 1})
        else:
            result.update({"toothbrush": 0})

        tb_state = STATES.get(state, "unknown state " + str(state))
        tb_mode = MODES.get(mode, "unknown mode " + str(mode))

        if sector == 254:
            tb_sector = "last sector"
        elif sector == 255:
            tb_sector = "no sector"
        else:
            tb_sector = "sector " + str(sector)

        result.update({
            "toothbrush state": tb_state,
            "pressure": pressure,
            "counter": counter,
            "mode": tb_mode,
            "sector": tb_sector,
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
    if self.discovery is False and oral_b_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(oral_b_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": ''.join(f'{i:02X}' for i in oral_b_mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result


def to_mac(addr: int):
    """Return formatted MAC address"""
    return ':'.join(f'{i:02X}' for i in addr)
