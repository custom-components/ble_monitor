"""The tests for the Brifit ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestBrifit:
    """Tests for the Brifit parser"""
    def test_brifit(self):
        """Test brifit parser."""
        data_string = "043E2B0201000085B07438C1A41F05095432303102010614FF55AA0101A4C13874B08501070A1D10F064000100D6"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"], "Brifit"
        assert sensor_msg["type"], "T201"
        assert sensor_msg["mac"], "A4C13874B085"
        assert sensor_msg["packet"], "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"], 25.89
        assert sensor_msg["humidity"], 43.36
        assert sensor_msg["voltage"], 2.63
        assert sensor_msg["battery"], 100
        assert sensor_msg["rssi"], -42
