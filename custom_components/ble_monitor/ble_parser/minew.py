"""Parser for Minew BLE advertisements"""
from __future__ import annotations

import logging
from struct import unpack
from typing import Any

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)

MINEW_FRAME_TYPE = 0xA1
E9_TEMPERATURE_VERSION = 0x13
E9_TEMPERATURE_LENGTH = 15


def parse_minew(self, data: bytes, mac: bytes) -> dict[str, Any] | None:
    """Parser for Minew sensor beacons.

    Minew sends several frames under frame type 0xA1 (info, acceleration, ...),
    told apart by the version byte after it. Only the E9 temperature frame (0x13)
    is supported; its temperature is signed 8.8 fixed-point in °C.

    Frame layout as decoded by reelyActive's advlib-ble-services (MIT):
    https://github.com/reelyactive/advlib-ble-services/blob/master/lib/minew.js
    """
    if (
        len(data) == E9_TEMPERATURE_LENGTH
        and data[4] == MINEW_FRAME_TYPE
        and data[5] == E9_TEMPERATURE_VERSION
    ):
        (battery, temp) = unpack(">Bh", data[6:9])
        return {
            "mac": to_unformatted_mac(mac),
            "type": "E9",
            "firmware": "Minew",
            "temperature": round(temp / 256, 2),
            "battery": battery,
            "data": True,
        }
    if self.report_unknown == "Minew":
        _LOGGER.info(
            "BLE ADV from UNKNOWN Minew DEVICE: MAC: %s, ADV: %s",
            to_mac(mac),
            data.hex(),
        )
    return None
