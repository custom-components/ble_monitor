"""The tests for the Blustream ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestBlustream:
    """Tests for the TestBlustream parser"""
    def test_blustream_taylorsense(self):
        """Test Blustream parser for Blustream."""
        data_string = "043E3102010000DEF902101A0C250201060CFF940101DEF902BE0FF107D0020AFE11067126001F369264BCE6115BFC365D9302DE"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Blustream"
        assert sensor_msg["type"] == "Blustream"
        assert sensor_msg["mac"] == "0C1A1002F9DE"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 20.0
        assert sensor_msg["humidity"] == 40.81
        assert sensor_msg["acceleration"] == 190
        assert sensor_msg["rssi"] == -34
