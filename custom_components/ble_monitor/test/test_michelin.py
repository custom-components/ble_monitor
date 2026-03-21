"""The tests for the Michelin TMS ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestMichelin:
    """Tests for the Michelin TMS parser"""
    def test_parse_michelin_tms(self):
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
