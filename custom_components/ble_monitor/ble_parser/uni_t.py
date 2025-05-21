"""Parser for UNI‑T UT363‑BT anemometer adverts"""
from __future__ import annotations
import logging
from datetime import datetime
from .helpers import to_unformatted_mac

_LOGGER = logging.getLogger(__name__)

_FACTORS = {          # convert everything to m/s
    40: 1.0,               # m/s
    50: 1 / 3.6,           # km/h
    60: 0.00508,           # ft/min
    70: 0.514444,          # kt
    80: 0.44704,           # mph
    90: 0.3048,            # ft/s
}
def parse_uni_t(self, mfg: bytes, mac: bytes) -> dict | None:
    """Return dict with wind_speed (m/s) and temperature (°C)."""
    _LOGGER.debug(f"UNI-T raw mfg data: {mfg.hex()}")
    try:
        txt = mfg[5:16].decode(errors="ignore")          # "  1.52M/S60"
        sp_txt, uc_txt = txt.split("M/S")
        speed = float(sp_txt) * _FACTORS.get(int(uc_txt), 1.0)
        temp  = round(int.from_bytes(mfg[16:18], "little") / 10.0, 1)
        pkt   = mfg[3]
    except Exception as err:
        _LOGGER.debug("UNI‑T decode failed: %s", err)
        return None

    return {
        "mac":         to_unformatted_mac(mac),
        "type":        "UNI‑T",
        "firmware":    "UT363BT",
        "packet":      pkt,
        "wind_speed":  round(speed, 2),
        "temperature": temp,
        "data":        True,
        "rssi":        self.rssi,
        "timestamp":   datetime.utcnow().isoformat(),
    }
