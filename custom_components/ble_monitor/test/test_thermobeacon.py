"""The tests for the Thermobeacon ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestThermobeacon:
    """Tests for the Thermobeacon parser"""
    def test_thermobeacon_smart_hygrometer(self):
        """Test thermobeacon Smart hygrometer parser."""
        data_string = "043e29020100002716000088061d0201060302f0ff15ff110000002716000088063c0c8f01a103b9d70300c8"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Thermobeacon"
        assert sensor_msg["type"] == "Smart hygrometer"
        assert sensor_msg["mac"] == "068800001627"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 24.9375
        assert sensor_msg["humidity"] == 58.0625
        assert sensor_msg["voltage"] == 3.132
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -56

    def test_thermobeacon_Lanyard_mini_hygrometer(self):
        """Test thermobeacon Lanyard/mini hygrometer parser."""
        data_string = "043e2902010000dc0e0000f1701d0201060302f0ff15ff10000000dc0e0000f1706a0b8101d70283270500b2"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Thermobeacon"
        assert sensor_msg["type"] == "Lanyard/mini hygrometer"
        assert sensor_msg["mac"] == "70F100000EDC"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 24.0625
        assert sensor_msg["humidity"] == 45.4375
        assert sensor_msg["voltage"] == 2.922
        assert sensor_msg["battery"] == 92.2
        assert sensor_msg["rssi"] == -78

    def test_T201(self):
        """Test thermobeacon brifit T201 parser."""
        data_string = "043E2B0201000085B07438C1A41F05095432303102010614FF55AA0101A4C13874B08501070A1D10F064000100D6"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"], "Thermobeacon"
        assert sensor_msg["type"], "T201"
        assert sensor_msg["mac"], "A4C13874B085"
        assert sensor_msg["packet"], "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"], 25.89
        assert sensor_msg["humidity"], 43.36
        assert sensor_msg["voltage"], 2.63
        assert sensor_msg["battery"], 100
        assert sensor_msg["rssi"], -42
