"""Parser for UNI‑T UT363BT advertisements"""

from __future__ import annotations

import logging
from datetime import datetime                # only used for the packet counter
from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


UNIT_MAP = {
    40: "m/s",
    50: "km/h",
    60: "ft/min",
    70: "knots",
    80: "mph",
    90: "ft/s",
}

# --- core parser -----------------------------------------------------------
def parse_uni_t(self, mfg_data: bytes, mac: bytes):
    """
    Parse manufacturer specific data from UNI‑T UT363BT anemometer.

    Payload layout (all fixed‑width):
        0‑1  : 0xBBAA      – company ID  (little‑endian)
        2‑4  : 10 05 37    – header / rolling counter
        5‑13 : ASCII "  1.52M/S60"
        14‑15: little‑endian temperature   -> raw / 44.5  = °C   (needs 2nd sample)
        16   : checksum    (simple sum & 0xFF)
    """

    device_type = "UNI‑T"
    firmware    = "UT363BT"
    packet_id   = mfg_data[3]               # rolling counter in the header
    adv_prio    = 5                         # low – it’s a passive advert

    # 1. Wind speed and unit
    ascii_block = mfg_data[5:16].decode(errors="ignore")  # "  1.52M/S60"
    speed_txt, unit_code_txt = ascii_block.split("M/S")
    speed_val  = float(speed_txt)
    unit_code  = int(unit_code_txt)
    unit       = UNIT_MAP.get(unit_code, "m/s")

    # Convert *everything* we expose to standard SI (m/s) so dashboards compare nicely
    CONVERT = {
        40: 1.0,
        50: 1 / 3.6,
        60: 0.00508,
        70: 0.514444,
        80: 0.44704,
        90: 0.3048,
    }
    speed_ms = speed_val * CONVERT.get(unit_code, 1.0)

    # 2. Temperature
    raw_temp = int.from_bytes(mfg_data[14:16], "little")
    temp_c   = raw_temp / 44.5                                    # empirical factor

    result = {
        "mac":       to_unformatted_mac(mac),
        "type":      device_type,
        "firmware":  firmware,
        "packet":    packet_id,
        "wind_speed": speed_ms,
        "temperature": round(temp_c, 1),
        "data":      True,
        "rssi":      self.rssi,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # --- de‑duplication bookkeeping (same pattern as ATC / Ruuvi parsers) ----
    try:
        prev_pkt = self.lpacket_ids[mac]
    except KeyError:
        prev_pkt = None

    if self.filter_duplicates and prev_pkt == packet_id:
        return None

    self.lpacket_ids[mac]   = packet_id
    self.adv_priority[mac]  = adv_prio

    return result
