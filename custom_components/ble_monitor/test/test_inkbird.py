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

    def test_inkbird_IBS_TH2(self):
        """Test Inkbird parser for Inkbird IBS-TH2."""
        data_string = "043e1c020104007a63000842491004097370730aff9c08f41000ba4e6408cc"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Inkbird"
        assert sensor_msg["type"] == "IBS-TH2"
        assert sensor_msg["mac"] == "49420800637A"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 22.04
        assert sensor_msg["humidity"] == 43.4
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -52
