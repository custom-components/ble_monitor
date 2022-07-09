"""The tests for the Laica Smart Scale ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestLaica:
    """Tests for the Laica parser"""
    def test_laica(self):
        """Test Laica parser."""
        data_string = "043e2b02010300a02bbe5e91a01f0201040303b0ff0fffaca0a02bbe5e91a0a02c92140dbf0709414141303032d9"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Laica"
        assert sensor_msg["type"] == "Laica Smart Scale"
        assert sensor_msg["mac"] == "A0915EBE2BA0"
        assert sensor_msg["packet"] == "a02bbe5e91a0a02c92140dbf"
        assert sensor_msg["data"]
        assert sensor_msg["weight"] == 13.0
        assert sensor_msg["rssi"] == -39
