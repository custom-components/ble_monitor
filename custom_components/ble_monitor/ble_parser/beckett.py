"""Parser for Beckett BLE advertisements"""

import logging
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import List, Optional

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)

# SEE https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Assigned_Numbers/out/en/Assigned_Numbers.pdf
# R.W. Beckett Corporation      0x061A
MFG_BLE_ID = 0x061A  # 1562
BOOTLOADER_MASK = 0x8000  # 32768


class BeckettException(Exception):
    pass


class BeckettProductKey(IntEnum):
    Unknown = 0
    Genisys75xx = 1
    GenisysOil = 1
    Iot7653 = 2
    Genisys7505 = 3
    LegacyGenisys = 3
    Iot7652 = 4
    BeckettLinkPro = 4
    GenisysGas = 5


class Genisys7505EndCause(Enum):
    NoEndCauseReported = "NoEndCauseReported"
    CFHEnded = "CFHEnded"
    FlameLoss = "FlameLoss"
    PumpPrime = "PumpPrime"
    ManualShutdown = "ManualShutdown"
    LowVoltage = "LowVoltage"
    DidNotLight = "DidNotLight"
    FlameEndOfPretime = "FlameEndOfPretime"
    RelayFailure = "RelayFailure"


# Primary and fallback end-cause labels for Genisys7505
_primary_end_causes: List[Optional[Genisys7505EndCause]] = [
    Genisys7505EndCause.NoEndCauseReported,
    Genisys7505EndCause.CFHEnded,
    Genisys7505EndCause.FlameLoss,
    None,
    Genisys7505EndCause.PumpPrime,
    Genisys7505EndCause.ManualShutdown,
    Genisys7505EndCause.LowVoltage,
    Genisys7505EndCause.NoEndCauseReported,
]

_fallback_end_causes: List[Genisys7505EndCause] = [
    Genisys7505EndCause.DidNotLight,
    Genisys7505EndCause.FlameLoss,
    Genisys7505EndCause.FlameEndOfPretime,
    Genisys7505EndCause.RelayFailure,
]


def _choose_end_cause(code: int) -> Genisys7505EndCause:
    """
    - Try primary using lower 3 bits
    - Otherwise use fallback using bits 3–4
    """
    index_primary = code & 0x07
    primary_label = _primary_end_causes[index_primary]
    if primary_label is not None:
        return primary_label
    index_fallback = (code & 0x18) >> 3
    return _fallback_end_causes[index_fallback]


def _get_base_device_product_key(value: int) -> BeckettProductKey:
    """Clears the BOOTLOADER_MASK bit to get the base product key."""
    base_key_value = value & ~BOOTLOADER_MASK
    return BeckettProductKey(base_key_value)


class GenisysLegacyState(IntEnum):
    Standby = 1
    MotorRelayTest = 2
    Prepurge = 3
    TFI = 4
    CarryOver = 5
    Run = 6
    PostPurge = 7
    Recycle = 8
    Lockout = 9
    PumpPrime = 10
    MotorRelayFeedbackTest = 11
    NoIgnitionPrePurge = 12


class GenisysDeviceNameKey(IntEnum):
    Genisys_7505_7575 = 0
    Genisys_7556 = 64
    Genisys_7559 = 96
    Genisys_7580 = 128


@dataclass
class BeckettMfgData:
    product_id: BeckettProductKey
    is_bootloader: bool
    device_name_key: GenisysDeviceNameKey
    advertisement_version: int
    connectable: bool
    raw_data: List[int] = field(default_factory=list)
    serial: Optional[int] = None
    # Optional LegacyGenisys fields
    state: Optional[GenisysLegacyState] = None
    last_end_cause: Optional[Genisys7505EndCause] = None
    cycle_count: Optional[int] = None


def unwrap_mfg_data(mfg_data: bytes) -> Optional[BeckettMfgData]:
    """
    - Prepends the 2-byte manufacturer ID [0x06, 0x1A] (1562)
    - Runs a simple XOR-based unwrapping on the payload
    - Interprets header fields and returns an BeckettMfgData instance
    """

    # Prepend the 2-byte manufacturer ID 0x061A
    # wrapped = _prepend_bytes(mfg_data, [0x06, 0x1A])
    # NO - BLEAK STRIPS THEM; HASS DOES NOT
    # https://github.com/hbldh/bleak/blob/b8d89fb63e54e0bddba72df93bbc4af355e2d131/bleak/backends/corebluetooth/scanner.py#L120
    # `manufacturer_value = bytes(manufacturer_binary_data[2:])`

    # HASS length is 28; BLEAK length is 24 but needed padding of 2
    wrapped = mfg_data[2:]

    # Perform the XOR "unwrap" loop starting at offset 4
    unwrapped: List[int] = []
    u = wrapped[2]
    o = wrapped[3]
    for idx in range(4, len(wrapped)):
        v = wrapped[idx]
        xored = v ^ (u + (idx - 2)) ^ o
        unwrapped.append(xored & 0xFF)
        u, o = o, v

    buf = bytes(unwrapped)
    length = len(buf)

    # The last byte is advertisementVersion
    adv_version = buf[-1]
    serial_num: Optional[int] = None
    if adv_version == 1 and length >= 20:
        serial_num = int.from_bytes(buf[16:20], "big")

    # Read D = uint16 at offset 0 (big-endian)
    D = int.from_bytes(buf[0:2], "big")
    product_key = _get_base_device_product_key(D)
    is_boot = bool(D & BOOTLOADER_MASK)
    _device_name_key = int.from_bytes(buf[2:4], "big")

    return BeckettMfgData(
        product_id=product_key,
        is_bootloader=is_boot,
        device_name_key=GenisysDeviceNameKey(_device_name_key),
        advertisement_version=adv_version,
        connectable=(buf[-2] == 0),
        raw_data=unwrapped,
        serial=serial_num,
    )


def _parse_legacy_genisys_state(info: BeckettMfgData) -> Optional[BeckettMfgData]:
    if info.product_id == BeckettProductKey.LegacyGenisys:
        raw = info.raw_data
        state = int.from_bytes(bytes(raw[4:6]), "big")
        end_cause_code = int.from_bytes(bytes(raw[6:8]), "big")
        cycle_ct = int.from_bytes(bytes(raw[8:10]), "big")

        info.state = GenisysLegacyState(state)
        info.last_end_cause = _choose_end_cause(end_cause_code)
        info.cycle_count = cycle_ct
        return info

    return None


def parse_mfg_data(raw_bytes: bytes) -> BeckettMfgData:
    """
    Parses manufacturer-specific advertisement data.
    Returns an BeckettMfgData instance with parsed fields,
    including state information for LegacyGenisys devices if applicable.
    """
    mfg_info = unwrap_mfg_data(raw_bytes)

    extended = _parse_legacy_genisys_state(mfg_info)
    return extended if extended is not None else mfg_info


def _cast_hass_output(mfg: BeckettMfgData) -> dict:
    hass_device_type = mfg.product_id.name
    return {
        "firmware": "Beckett",
        "data": True,
        "packet": "no packet id",
        "type": hass_device_type,
        "burner_product": mfg.product_id.name,
        "burner_device": mfg.device_name_key.name,
        "burner_serial": mfg.serial,
        "burner_is_bootloader": mfg.is_bootloader,
        "burner_advertisement_version": mfg.advertisement_version,
        "burner_connectable": mfg.connectable,
        "burner_state": mfg.state.name if mfg.state is not None else None,
        "burner_last_end_cause": (
            mfg.last_end_cause.name if mfg.last_end_cause is not None else None
        ),
        "burner_cycle_count": mfg.cycle_count,
    }


# HomeAssistant integration
def parse_beckett(self, data: str, mac: bytes):
    """RW Beckett Corp parser: MyTechnician, BeckettLink Pro 7652a, Genisys"""
    try:
        mfg_data: BeckettMfgData = parse_mfg_data(data)
        _LOGGER.debug(f"Parsed Beckett Genisys ADV: {mfg_data}")
        result = _cast_hass_output(mfg_data)
        result.update(
            {
                "mac": to_unformatted_mac(mac),
            }
        )
    except Exception:
        _LOGGER.warning("Error parsing Beckett manufacturer data:", exc_info=True)
        #raise
        return None

    #### BOILERPLATE
    if self.report_unknown == "Beckett":
        _LOGGER.info(
            f"BLE ADV from UNKNOWN Beckett DEVICE: MAC: {to_mac(mac)}, ADV: {data.hex()}",
        )
        return None

    return result
