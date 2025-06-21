"""The tests for the MOCREO ble_parser."""
import datetime

from ble_monitor.ble_parser import BleParser


class TestMOCREO:
    """Tests for the MOCREO parser"""

    def test_MOCREO_ST5(self):
        """Test MOCREO parser for ST5."""
        data_string = "043e2b02010001bbaa00a4ae301f02010607094d4f4352454f13ff0181290154b0920900000000006162000000c5"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "MOCREO"
        assert sensor_msg["type"] == "ST5"
        assert sensor_msg["mac"] == "30AEA400AABB"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["temperature"] == 24.5
        assert sensor_msg["battery"] == 84
        assert sensor_msg["data"]
        assert sensor_msg["rssi"] == -59

    def test_MOCREO_ST6(self):
        """Test MOCREO parser for ST6."""
        data_string = "043e2b02010001bbaa00a4ae301f02010607094d4f4352454f13ff4183dd0262b0200af31400000150bf000000c0"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)
        assert sensor_msg["firmware"] == "MOCREO"
        assert sensor_msg["type"] == "ST6"
        assert sensor_msg["mac"] == "30AEA400AABB"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["temperature"] == 25.92
        assert sensor_msg["humidity"] == 53.63
        assert sensor_msg["battery"] == 98
        assert sensor_msg["data"]
        assert sensor_msg["rssi"] == -64

    def test_MOCREO_ST8(self):
        """Test MOCREO parser for ST8."""
        data_string = "043e2b02010001bbaa00a4ae301f02010607094d4f4352454f13ff1184e98264b05a0a00000000000a64000000e2"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)
        assert sensor_msg["firmware"] == "MOCREO"
        assert sensor_msg["type"] == "ST8"
        assert sensor_msg["mac"] == "30AEA400AABB"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["temperature"] == 26.5
        assert sensor_msg["battery"] == 100
        assert sensor_msg["data"]
        assert sensor_msg["rssi"] == -30

    def test_MOCREO_ST9(self):
        """Test MOCREO parser for ST9."""
        data_string = "043e2b02010001bbaa00a4ae301f02010607094d4f4352454f13ff01867301c8b08c0aa713000000a20c000000b6"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)
        assert sensor_msg["firmware"] == "MOCREO"
        assert sensor_msg["type"] == "ST9"
        assert sensor_msg["mac"] == "30AEA400AABB"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["temperature"] == 27.0
        assert sensor_msg["humidity"] == 50.31
        assert sensor_msg["battery"] == 72
        assert sensor_msg["data"]
        assert sensor_msg["rssi"] == -74

    def test_MOCREO_ST10(self):
        """Test MOCREO parser for ST10."""
        data_string = "043e2b02010001bbaa00a4ae301f02010607094d4f4352454f13ff0187890181b092f70000000000da73000000f0"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)
        assert sensor_msg["firmware"] == "MOCREO"
        assert sensor_msg["type"] == "ST10"
        assert sensor_msg["mac"] == "30AEA400AABB"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["temperature"] == -21.58
        assert sensor_msg["battery"] == 1
        assert sensor_msg["data"]
        assert sensor_msg["rssi"] == -16

    def test_MOCREO_MS1(self):
        """Test MOCREO parser for MS1."""
        data_string = "043e2b02010001bbaa00a4ae301f02010607094d4f4352454f13ff418b0a00e4b0730a00000000000040000000d3"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)
        assert sensor_msg["firmware"] == "MOCREO"
        assert sensor_msg["type"] == "MS1"
        assert sensor_msg["mac"] == "30AEA400AABB"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["temperature"] == 26.75
        assert sensor_msg["battery"] == 100
        assert sensor_msg["data"]
        assert sensor_msg["rssi"] == -45


    def test_MOCREO_MS2(self):
        """Test MOCREO parser for MS2."""
        data_string = "043e2b02010001bbaa00a4ae301f02010607094d4f4352454f13ff018d7b00e4b0370a6212000000002e000000d6"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)
        assert sensor_msg["firmware"] == "MOCREO"
        assert sensor_msg["type"] == "MS2"
        assert sensor_msg["mac"] == "30AEA400AABB"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["temperature"] == 26.15
        assert sensor_msg["humidity"] == 47.06
        assert sensor_msg["battery"] == 100
        assert sensor_msg["data"]
        assert sensor_msg["rssi"] == -42

    def test_MOCREO_SW2(self):
        """Test MOCREO parser for SW2."""
        data_string = "043e2b02010001bbaa00a4ae301f02010607094d4f4352454f13ff01821580e4000000000000000086f6000000c1"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)
        assert sensor_msg["firmware"] == "MOCREO"
        assert sensor_msg["type"] == "SW2"
        assert sensor_msg["mac"] == "30AEA400AABB"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["water leak"] == 0
        assert sensor_msg["battery"] == 100
        assert sensor_msg["data"]
        assert sensor_msg["rssi"] == -63
