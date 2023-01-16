"""The tests for the Jaalee ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestJaalee:
    """Tests for the Jaalee parser"""
    def test_jaalee_jht(self):
        """Test Tilt parser for Jaalee JHT."""
        data_string = "043e4a02010000138581ff9fd03e0201041bff4c000215ebefd08370a247c89837e7b5634df5256c6ca36ecb60030325f50e1625f560138581ff9fd06c6ca36e000000000000000000000000cc"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Jaalee"
        assert sensor_msg["type"] == "JHT"
        assert sensor_msg["mac"] == "D09FFF818513"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 27.57
        assert sensor_msg["humidity"] == 73.8
        assert sensor_msg["rssi"] == -52
