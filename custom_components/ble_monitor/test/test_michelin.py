"""The tests for the Michelin TMS ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestMichelin:
    """Tests for the Michelin TMS parser"""
    def test_parse_michelin_tms_frame_type_3_4(self):
        data_string = "043e2102010300e07c03a703bc1502010611ff280801034fc8d403505643017d511e00bc"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "TMS"
        assert sensor_msg["type"] == "TMS"
        assert sensor_msg["mac"] == "BC03A7037CE0"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"] == True
        assert sensor_msg["temperature"] == 19
        assert sensor_msg["voltage"] == 3.0
        assert sensor_msg["pressure"] == 980
        assert sensor_msg["count"] == 1986941
        assert sensor_msg["steps"] == 1
        assert sensor_msg["text"] == "PVC"
        assert sensor_msg["rssi"] == -68

    def test_parse_michelin_tms_frame_type_f(self):
        data_string = "043e2302010300e6b706a703bc1802010614ff2808010f0801c7ed03e6b706a703bca5a80100b9"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "TMS"
        assert sensor_msg["type"] == "TMS"
        assert sensor_msg["mac"] == "BC03A706B7E6"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"] == True
        assert sensor_msg["temperature"] == 26.4
        assert sensor_msg["voltage"] == 2.99
        assert sensor_msg["pressure"] == 1005
        assert sensor_msg["count"] == 108709
        assert sensor_msg["steps"] == 1
        assert sensor_msg["text"] == ""
        assert sensor_msg["rssi"] == -71


    def test_parse_michelin_tms_too_short_returns_cleanly(self):
        """A Michelin TMS advertisement shorter than the required payload must not raise."""
        data_string = "043e1402010300e07c03a703bc0802010604ff280801bc"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg is None
