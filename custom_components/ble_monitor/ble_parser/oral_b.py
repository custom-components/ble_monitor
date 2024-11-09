"""Parser for Oral-B BLE advertisements."""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)

STATES = {
    0: "unknown",
    1: "initializing",
    2: "idle",
    3: "running",
    4: "charging",
    5: "setup",
    6: "flight menu",
    8: "selection menu",
    113: "final test",
    114: "pcb test",
    115: "sleeping",
    116: "transport"
}

PRESSURE = {
    114: "normal",
    118: "button pressed",
    178: "high"
}


def parse_oral_b(self, data: bytes, mac: bytes):
    """Parser for Oral-B toothbrush."""
    msg_length = len(data)
    firmware = "Oral-B"
    result = {"firmware": firmware}
    if msg_length == 15:
        (state, pressure, counter, mode, sector, sector_timer, no_of_sectors) = unpack(
            ">BBHBBBB", data[7:15]
        )

        if state == 3:
            result.update({"toothbrush": 1})
        else:
            result.update({"toothbrush": 0})

        device_bytes = data[4:7]
        if device_bytes == b'\x062k':
            device_type = "IO Series 7"
            MODES = {
                0: "daily clean",
                1: "sensitive",
                2: "gum care",
                3: "whiten",
                4: "intense",
                8: "settings"
            }
        else:
            device_type = "SmartSeries 7000"
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

        tb_state = STATES.get(state, "unknown state " + str(state))
        tb_mode = MODES.get(mode, "unknown mode " + str(mode))
        tb_pressure = PRESSURE.get(pressure, "unknown pressure " + str(pressure))

        if sector == 254:
            tb_sector = "last sector"
        elif sector == 255:
            tb_sector = "no sector"
        else:
            tb_sector = "sector " + str(sector)

        result.update({
            "toothbrush state": tb_state,
            "pressure": tb_pressure,
            "counter": counter,
            "mode": tb_mode,
            "sector": tb_sector,
            "sector timer": sector_timer,
            "number of sectors": no_of_sectors,
        })

    else:
        if self.report_unknown == "Oral-B":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Oral-B DEVICE: MAC: %s, ADV: %s",
                to_mac(mac),
                data.hex()
            )
        return None

    result.update({
        "mac": to_unformatted_mac(mac),
        "type": device_type,
        "packet": "no packet id",
        "firmware": firmware,
        "data": True
    })
    return result
