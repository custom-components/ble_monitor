"""Constants for BTHome measurements."""
import dataclasses
from typing import Optional


@dataclasses.dataclass
class MeasTypes:
    meas_format: str
    unit_of_measurement: Optional[str] = None
    data_length: int = 1
    data_format: str = "unsigned_integer"
    factor: float = 1


MEAS_TYPES: dict[int, MeasTypes] = {
    0x01: MeasTypes(
        meas_format="battery",
        unit_of_measurement="%",
    ),
    0x02: MeasTypes(
        meas_format="temperature",
        unit_of_measurement="°C",
        data_length=2,
        data_format="signed_integer",
        factor=0.01,
    ),
    0x03: MeasTypes(
        meas_format="humidity",
        unit_of_measurement="%",
        data_length=2,
        factor=0.01,
    ),
    0x04: MeasTypes(
        meas_format="pressure",
        unit_of_measurement="mbar",
        data_length=3,
        factor=0.01,
    ),
    0x05: MeasTypes(
        meas_format="pressure",
        unit_of_measurement="hPa",
        data_length=3,
        factor=0.01,
    ),
    0x06: MeasTypes(
        meas_format="weight",
        unit_of_measurement="kg",
        data_length=2,
        factor=0.01,
    ),
    0x07: MeasTypes(
        meas_format="weight",
        unit_of_measurement="lbs",
        data_length=2,
        factor=0.01,
    ),
    0x08: MeasTypes(
        meas_format="dewpoint",
        unit_of_measurement="°C",
        data_length=2,
        data_format="signed_integer",
        factor=0.01,
    ),
    0x09: MeasTypes(
        meas_format="count",
        unit_of_measurement="1",
        data_length=1,
    ),
    0x0A: MeasTypes(
        meas_format="energy",
        unit_of_measurement="kWh",
        data_length=3,
        factor=0.001,
    ),
    0x0B: MeasTypes(
        meas_format="power",
        unit_of_measurement="W",
        data_length=3,
        factor=0.01,
    ),
    0x0C: MeasTypes(
        meas_format="voltage",
        unit_of_measurement="V",
        data_length=2,
        factor=0.001,
    ),
    0x0D: MeasTypes(
        meas_format="pm2.5",
        unit_of_measurement="µg/m³",
        data_length=2,
    ),
    0x0E: MeasTypes(
        meas_format="pm10",
        unit_of_measurement="µg/m³",
        data_length=2,
    ),
    0x0F: MeasTypes(
        meas_format="binary",
    ),
    0x10: MeasTypes(
        meas_format="switch",
    ),
    0x11: MeasTypes(
        meas_format="opening",
    ),
    0x12: MeasTypes(
        meas_format="co2",
        unit_of_measurement="ppm",
        data_length=2,
    ),
    0x13: MeasTypes(
        meas_format="tvoc",
        unit_of_measurement="µg/m³",
        data_length=2,
    ),
    0x14: MeasTypes(
        meas_format="moisture",
        unit_of_measurement="%",
        data_length=2,
        factor=0.01,
    ),
}
