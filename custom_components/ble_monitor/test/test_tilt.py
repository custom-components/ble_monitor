"""The tests for the Tilt ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestTilt:
    """Tests for the Tilt parser"""
    def test_tilt_red(self):
        """Test Tilt parser for Tilt Red."""
        data_string = "043E27020100005A099B16A3041B1AFF4C000215A495BB10C5B14B44B5121370F02D74DE004403F8C5C7"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Tilt"
        assert sensor_msg["type"] == "Tilt Red"
        assert sensor_msg["mac"] == "04A3169B095A"
        assert sensor_msg["uuid"] == "a495bb10c5b14b44b5121370f02d74de"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 20.0
        assert sensor_msg["gravity"] == 1.016
        assert sensor_msg["rssi"] == -57
