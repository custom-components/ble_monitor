"""Parser for Chef iQ BLE advertisements."""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


# CQ60 firmware emits these sentinel values when a probe ring has nothing
# to read (probe partially inserted, broken probe wire, ring not in
# contact with food). They decode as ~3,276 °C if treated as a real value,
# which trips HA's temperature device-class limits and produces nonsense
# graphs / alerts. Mask them to ``None`` so the entity reads as
# ``unavailable`` instead.
TEMP_SENTINEL_MIN = 0x7FF0


def _decode_temp(raw: int) -> float | None:
    """Decode a little-endian uint16 temperature in tenths of °C."""
    if raw >= TEMP_SENTINEL_MIN:
        return None
    return round(raw / 10, 1)


def parse_chefiq(self, data: str, mac: bytes):
    """Parse Chef iQ advertisement."""
    msg_length = len(data)
    firmware = "Chef iQ"
    msg = data[6:]
    if msg_length == 22:
        # Chef iQ CQ60
        device_type = "CQ60"
        (batt, temp_probe_3, _, temp_meat, temp_tip, temp_probe_1, temp_probe_2, temp_ambient, _) = unpack(
            "<BBHHHHHHh", msg
        )
        log_cnt = "no packet id"
        result = {
            "battery": batt,
            "meat temperature": _decode_temp(temp_meat),
            "temperature probe tip": _decode_temp(temp_tip),
            "temperature probe 1": _decode_temp(temp_probe_1),
            "temperature probe 2": _decode_temp(temp_probe_2),
            # Probe 3 is an 8-bit °C value (no /10 scaling).
            # 0xFE / 0xFF are the disconnected sentinels.
            "temperature probe 3": (
                float(temp_probe_3) if temp_probe_3 < 0xFE else None
            ),
            "ambient temperature": _decode_temp(temp_ambient),
        }
    else:
        if self.report_unknown == "Chef iQ":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Chef iQ DEVICE: MAC: %s, ADV: %s",
                to_mac(mac),
                data.hex()
            )
        return None

    result.update({
        "mac": to_unformatted_mac(mac),
        "type": device_type,
        "packet": log_cnt,
        "firmware": firmware,
        "data": True
    })
    return result
