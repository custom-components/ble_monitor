"""The tests for the Thermoplus ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestThermoplus:

    def test_thermoplus_smart_hygrometer(self):
        """Test thermoplus Smart hygrometer parser."""
        data_string = "043e29020100002716000088061d0201060302f0ff15ff110000002716000088063c0c8f01a103b9d70300c8"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Thermoplus"
        assert sensor_msg["type"] == "Smart hygrometer"
        assert sensor_msg["mac"] == "068800001627"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 24.9375
        assert sensor_msg["humidity"] == 58.0625
        assert sensor_msg["voltage"] == 3.132
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -56

    def test_thermoplus_Lanyard_mini_hygrometer(self):
        """Test thermoplus Lanyard/mini hygrometer parser."""
        data_string = "043e2902010000dc0e0000f1701d0201060302f0ff15ff10000000dc0e0000f1706a0b8101d70283270500b2"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Thermoplus"
        assert sensor_msg["type"] == "Lanyard/mini hygrometer"
        assert sensor_msg["mac"] == "70F100000EDC"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 24.0625
        assert sensor_msg["humidity"] == 45.4375
        assert sensor_msg["voltage"] == 2.922
        assert sensor_msg["battery"] == 92.2
        assert sensor_msg["rssi"] == -78
