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
    0x00: MeasTypes(
        meas_format="packet",
    ),
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
        meas_format="illuminance",
        unit_of_measurement="lux",
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
    0x15: MeasTypes(
        meas_format="battery low",
    ),
    0x16: MeasTypes(
        meas_format="battery charging",
    ),
    0x17: MeasTypes(
        meas_format="carbon monoxide",
    ),
    0x18: MeasTypes(
        meas_format="cold",
    ),
    0x19: MeasTypes(
        meas_format="connectivity",
    ),
    0x1A: MeasTypes(
        meas_format="door",
    ),
    0x1B: MeasTypes(
        meas_format="garage door",
    ),
    0x1C: MeasTypes(
        meas_format="gas detected",
    ),
    0x1D: MeasTypes(
        meas_format="heat",
    ),
    0x1E: MeasTypes(
        meas_format="light",
    ),
    0x1F: MeasTypes(
        meas_format="lock",
    ),
    0x20: MeasTypes(
        meas_format="moisture detected",
    ),
    0x21: MeasTypes(
        meas_format="motion",
    ),
    0x22: MeasTypes(
        meas_format="moving",
    ),
    0x23: MeasTypes(
        meas_format="occupancy",
    ),
    0x24: MeasTypes(
        meas_format="plug",
    ),
    0x25: MeasTypes(
        meas_format="presence",
    ),
    0x26: MeasTypes(
        meas_format="problem",
    ),
    0x27: MeasTypes(
        meas_format="running",
    ),
    0x28: MeasTypes(
        meas_format="safety",
    ),
    0x29: MeasTypes(
        meas_format="smoke",
    ),
    0x2A: MeasTypes(
        meas_format="sound",
    ),
    0x2B: MeasTypes(
        meas_format="tamper",
    ),
    0x2C: MeasTypes(
        meas_format="vibration",
    ),
    0x2D: MeasTypes(
        meas_format="window",
    ),
    0x2E: MeasTypes(
        meas_format="humidity",
        unit_of_measurement="%",
    ),
    0x2F: MeasTypes(
        meas_format="moisture",
        unit_of_measurement="%",
    ),
    0x3A: MeasTypes(
        meas_format="button",
    ),
    0x3C: MeasTypes(
        meas_format="dimmer",
        data_length=2,
    ),
    0x3D: MeasTypes(
        meas_format="count",
        data_length=2,
    ),
    0x3E: MeasTypes(
        meas_format="count",
        data_length=4,
    ),
    0x3F: MeasTypes(
        meas_format="rotation",
        unit_of_measurement="°",
        data_length=2,
        data_format="signed_integer",
        factor=0.1,
    ),
    0x40: MeasTypes(
        meas_format="distance mm",
        unit_of_measurement="mm",
        data_length=2,
    ),
    0x41: MeasTypes(
        meas_format="distance",
        unit_of_measurement="m",
        data_length=2,
        factor=0.1,
    ),
    0x42: MeasTypes(
        meas_format="duration",
        unit_of_measurement="s",
        data_length=3,
        factor=0.001,
    ),
    0x43: MeasTypes(
        meas_format="current",
        unit_of_measurement="A",
        data_length=2,
        factor=0.001,
    ),
    0x44: MeasTypes(
        meas_format="speed",
        unit_of_measurement="m/s",
        data_length=2,
        factor=0.01,
    ),
    0x45: MeasTypes(
        meas_format="temperature",
        unit_of_measurement="°C",
        data_length=2,
        data_format="signed_integer",
        factor=0.1,
    ),
    0x46: MeasTypes(
        meas_format="uv index",
        data_length=1,
        factor=0.1,
    ),
    0x47: MeasTypes(
        meas_format="volume",
        unit_of_measurement="L",
        data_length=2,
        factor=0.1,
    ),
    0x48: MeasTypes(
        meas_format="volume mL",
        unit_of_measurement="mL",
        data_length=2,
    ),
    0x49: MeasTypes(
        meas_format="volume flow rate",
        unit_of_measurement="m3/h",
        data_length=2,
        factor=0.001,
    ),
    0x4A: MeasTypes(
        meas_format="voltage",
        unit_of_measurement="V",
        data_length=2,
        factor=0.1,
    ),
    0x4B: MeasTypes(
        meas_format="gas",
        unit_of_measurement="m3",
        data_length=3,
        factor=0.001,
    ),
    0x4C: MeasTypes(
        meas_format="gas",
        unit_of_measurement="m3",
        data_length=4,
        factor=0.001,
    ),
    0x4D: MeasTypes(
        meas_format="energy",
        unit_of_measurement="kWh",
        data_length=4,
        factor=0.001,
    ),
    0x4E: MeasTypes(
        meas_format="volume",
        unit_of_measurement="L",
        data_length=4,
        factor=0.001,
    ),
    0x4F: MeasTypes(
        meas_format="water",
        unit_of_measurement="L",
        data_length=4,
        factor=0.001,
    ),
    0x50: MeasTypes(
        meas_format="timestamp",
        data_length=4,
        data_format="timestamp",
    ),
    0x51: MeasTypes(
        meas_format="acceleration",
        unit_of_measurement="m/s²",
        data_length=2,
        factor=0.001,
    ),
    0x52: MeasTypes(
        meas_format="gyroscope",
        unit_of_measurement="°/s",
        data_length=2,
        factor=0.001,
    ),
    0x53: MeasTypes(
        meas_format="text",
        data_format="string",
    ),
}

BUTTON_EVENTS: dict[int, str | None] = {
    0x00: None,
    0x01: "press",
    0x02: "double press",
    0x03: "triple press",
    0x04: "long press",
    0x05: "long double press",
    0x06: "long triple press",
}

DIMMER_EVENTS: dict[int, str | None] = {
    0x00: None,
    0x01: "rotate left",
    0x02: "rotate right",
}
