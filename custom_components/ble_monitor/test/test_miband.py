"""The tests for the Mi Band ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestMiBand:
    """Tests for the Mi Band parser"""
    def test_miband(self):
        """Test Mi Band parser."""
        data_string = "043e390d011200004b0b893f09c50100ff7fb20000000000000000001f0201041bff5701020affffffffffffffffffffffffffffff03c5093f890b4b"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Mi Band"
        assert sensor_msg["type"] == "Mi Band"
        assert sensor_msg["mac"] == "C5093F890B4B"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["heart rate"] == 10
        assert sensor_msg["rssi"] == -78
