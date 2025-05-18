import logging

from custom_components.ble_monitor.ble_parser import BleParser, ParserManager

_LOGGER = logging.getLogger(__name__)

# map the two‐digit ASCII unit codes to m/s conversion lambdas
UNIT_CONVERSIONS = {
    b"40": lambda x: x,             # m/s
    b"50": lambda x: x / 3.6,       # km/h → m/s
    b"60": lambda x: x * 0.00508,   # ft/min → m/s
    b"70": lambda x: x * 0.514444,  # knots → m/s
    b"80": lambda x: x * 0.44704,   # mph → m/s
    b"90": lambda x: x * 0.3048,    # ft/s → m/s
}

@ParserManager.register_manufacturer(0xFF14)
class UniTParser(BleParser):
    """Parser for UNI-T UT363BT anemometer."""

    def __init__(self):
        super().__init__(
            name="UT363BT",
            manufacturer_id=0xFF14,
            device_name="UT363BT",
            ml=0x14,
        )

    def parse(self, data: bytearray):
        # data == the full manufacturer_data payload (AA BB 10 05 37 20 20 31 2E ... 6C)
        if len(data) < 16:
            return None

        try:
            # bytes 5..15 contain ASCII "  1.52M/S60"
            txt = data[5:16].decode("ascii", "ignore")
            speed_val = float(txt.split("M/S")[0])
            code = txt[-2:].encode("ascii")

            # convert to m/s
            speed_ms = UNIT_CONVERSIONS.get(code, UNIT_CONVERSIONS[b"40"])(speed_val)

            # temperature is the two bytes before the checksum, little-endian
            t_raw = int.from_bytes(data[-3:-1], "little")
            temp_c = t_raw / 44.5
        except Exception as e:
            _LOGGER.error("UT363BT parsing error: %s", e)
            return None

        return {
            "wind_speed": speed_ms,
            "temperature": temp_c,
        }
