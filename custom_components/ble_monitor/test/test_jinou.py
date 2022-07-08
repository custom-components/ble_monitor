"""The tests for the Jinou ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestJinou:
    """Tests for the Jinou parser"""
    def test_jinou_bc07_5_beacon(self):
        """Test Jinou parser for BC07-5 beacon"""
        data_string = "043e22020100009306bed281f816020106030220aa0eff00120700360264f881d2be0693db"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Jinou"
        assert sensor_msg["type"] == "BEC07-5"
        assert sensor_msg["mac"] == "F881D2BE0693"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 18.7
        assert sensor_msg["humidity"] == 54.2
        assert sensor_msg["rssi"] == -37
