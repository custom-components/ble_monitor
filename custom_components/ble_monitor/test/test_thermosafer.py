"""Tests for the Thermosafer BLE parser."""

from ble_monitor.ble_parser import BleParser
from ble_monitor.ble_parser.thermosafer import parse_thermosafer


class TestThermosafer:
    """Tests for the Thermosafer parser."""

    def test_thermosafer_7a0a5(self):
        """Parse observed advertising data in an extended report with a synthetic address."""
        data = bytes.fromhex(
            "043E390D011300000102030405060100FF7FF20000000000000000001F"
            "0201060302091817FF0EBC01070A000A05640CE400000000000000000000F0"
        )
        parser = BleParser()
        sensor_msg, tracker_msg = parser.parse_raw_data(data)

        assert tracker_msg is None
        assert sensor_msg["firmware"] == "Thermosafer"
        assert sensor_msg["type"] == "Thermosafer"
        assert sensor_msg["mac"] == "060504030201"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 33.0
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -14

    def test_invalid_manufacturer_data(self):
        """Reject malformed advertisements and out-of-range battery values."""
        data = bytes.fromhex("17ff0ebc01070a000a05640ce400000000000000000000f0")
        mac = bytes.fromhex("060504030201")
        assert parse_thermosafer(None, data[:-1], mac) is None
        assert parse_thermosafer(None, data[:4] + b"\x02" + data[5:], mac) is None
        assert parse_thermosafer(None, data[:10] + b"\x65" + data[11:], mac) is None
