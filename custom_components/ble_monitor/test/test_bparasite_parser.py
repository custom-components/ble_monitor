"""The tests for the b-parasite ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestBParasite:
    """Tests for the bparasite parser"""

    def test_bparasite_v2(self):
        """Test bparasite parser for v2 format (with illuminance)"""
        data_string = "043e2b020103010102caf0caf01f02010415161a18110b0aa1542cbca1fffff0caf0ca0201004205096e524635b8"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "b-parasite V1.1.0 (with illuminance)"
        assert sensor_msg["type"] == "b-parasite V1.1.0"
        assert sensor_msg["mac"] == "F0CAF0CA0201"
        assert sensor_msg["packet"] == 11
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 21.548
        assert sensor_msg["humidity"] == 73.68316650390625
        assert sensor_msg["voltage"] == 2.721
        assert sensor_msg["illuminance"] == 66
        assert sensor_msg["moisture"] == 99.99847412109375
        assert sensor_msg["rssi"] == -72

    def test_bparasite_v1(self):
        """Test bparasite parser for v1 format (without illuminance)"""
        data_string = "043e29020103010102caf0caf01d02010413161a18100b0aa1542cbca1fffff0caf0ca020105096e524635b8"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "b-parasite V1.0.0 (without illuminance)"
        assert sensor_msg["type"] == "b-parasite V1.0.0"
        assert sensor_msg["mac"] == "F0CAF0CA0201"
        assert sensor_msg["packet"] == 11
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 21.548
        assert sensor_msg["humidity"] == 73.68316650390625
        assert sensor_msg["voltage"] == 2.721
        assert sensor_msg["moisture"] == 99.99847412109375
        assert sensor_msg["rssi"] == -72
