"""The tests for the Michelin TMS ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestMichelin:
    """Tests for the Michelin TMS parser"""
    def test_parse_michelin_tms(self):
        data_string = "043E2002010000332211A703BC1B02010611FF2808010351C6C00350345301C6000000D1"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "TMS"
        assert sensor_msg["type"] == "TMS"
        assert sensor_msg["mac"] == "BC03A7112233"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"] == True
        assert sensor_msg["temperature"] == 22
        assert sensor_msg["voltage"] == 2.98
        assert sensor_msg["pressure"] == 960
        assert sensor_msg["count"] == 198
        assert sensor_msg["steps"] == 1
        assert sensor_msg["text"] == "P4S"
        assert sensor_msg["rssi"] == -47