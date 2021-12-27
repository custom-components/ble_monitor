"""The tests for the Inkbird ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestInkbird:
    """Tests for the Inkbird parser"""
    def test_inkbird_iBBQ_2_probes(self):
        """Test Inkbird parser for Inkbird iBBQ with 2 probes."""
        data_string = "043e23020100007bf4abb51434170201060302f0ff0fff000000003414b5abf47bc800d200e5"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Inkbird"
        assert sensor_msg["type"] == "iBBQ-2"
        assert sensor_msg["mac"] == "3414B5ABF47B"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature probe 1"] == 20.0
        assert sensor_msg["temperature probe 2"] == 21.0
        assert sensor_msg["rssi"] == -27
