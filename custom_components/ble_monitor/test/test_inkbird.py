"""The tests for the Inkbird ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestInkbird:
    """Tests for the Inkbird parser"""
    def test_inkbird_iBBQ_1_probes(self):
        """Test Inkbird parser for Inkbird iBBQ with 1 probe."""
        data_string = "043e2102010000d7652e9aec28150201060302f0ff0dff0000000028ec9a2e65d7f000b5"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Inkbird"
        assert sensor_msg["type"] == "iBBQ-1"
        assert sensor_msg["mac"] == "28EC9A2E65D7"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature probe 1"] == 24.0
        assert sensor_msg["rssi"] == -75

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

    def test_inkbird_iBBQ_4_probes(self):
        """Test Inkbird parser for Inkbird iBBQ with 4 probes."""
        data_string = "043e27020100001e6771c1e2a81b0201060302f0ff13ff00000000a8e2c171671e0000000000000000c2"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Inkbird"
        assert sensor_msg["type"] == "iBBQ-4"
        assert sensor_msg["mac"] == "A8E2C171671E"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature probe 1"] == 0
        assert sensor_msg["temperature probe 2"] == 0
        assert sensor_msg["temperature probe 3"] == 0
        assert sensor_msg["temperature probe 4"] == 0
        assert sensor_msg["rssi"] == -62


    def test_inkbird_iBBQ_6_probes(self):
        """Test Inkbird parser for Inkbird iBBQ with 6 probes."""
        data_string = "043e480d01130001593535d793180100ff7fa30000000000000000002e0201060302F0FF17FF000000001893D7353559D200F6FFF6FFF6FFF6FFF6FF050969424251051218003801020A00"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Inkbird"
        assert sensor_msg["type"] == "iBBQ-6"
        assert sensor_msg["mac"] == "1893D7353559"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature probe 1"] == 21.0
        assert sensor_msg["temperature probe 2"] == 0
        assert sensor_msg["temperature probe 3"] == 0
        assert sensor_msg["temperature probe 4"] == 0
        assert sensor_msg["rssi"] == -93

    def test_inkbird_IBS_TH(self):
        """Test Inkbird parser for Inkbird IBS-TH."""
        data_string = "043e1c020104007a63000842491004097370730aff9c08f41000ba4e6408cc"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Inkbird"
        assert sensor_msg["type"] == "IBS-TH"
        assert sensor_msg["mac"] == "49420800637A"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 22.04
        assert sensor_msg["humidity"] == 43.4
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -52

    def test_inkbird_IBS_TH2_T_only(self):
        """Test Inkbird parser for Inkbird IBS-TH2 (T only)."""
        data_string = "043e1c02010400561d000742491004097470730affff0700000031603306c5"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Inkbird"
        assert sensor_msg["type"] == "IBS-TH2 (T only)"
        assert sensor_msg["mac"] == "494207001D56"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 20.47
        assert sensor_msg["battery"] == 51
        assert sensor_msg["rssi"] == -59
