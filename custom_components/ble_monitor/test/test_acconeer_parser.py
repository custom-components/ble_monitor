"""The tests for the Acconeer ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestAcconeer:
    """Tests for the Acconeer parser"""
    def test_acconeer_xm122(self):
        """Test acconeer parser for Acconeer XM122."""
        data_string = "043e22020103013412b69009e01602010612ffc0ac806400160001000000000000000000c2"

        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Acconeer"
        assert sensor_msg["type"] == "Acconeer XM122"
        assert sensor_msg["mac"] == "E00990B61234"
        assert sensor_msg["packet"] == "6400160001000000000000000000"
        assert sensor_msg["data"]
        assert sensor_msg["battery"] == 100
        assert sensor_msg["temperature"] == 22
        assert sensor_msg["motion"] == 1
        assert sensor_msg["rssi"] == -62
