"""The tests for the Almendo ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestAlmendo:
    """Tests for the Almendo parser"""
    def test_almendo_blusensor_mini(self):
        """Test Almendo parser for bBluSensor mini."""
        data_string = "043e26020103010eba64c4f5fc1a02010613ffe806010a0a08011800fb09e511a6030f0203020a093d"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Almendo V1"
        assert sensor_msg["type"] == "bluSensor Mini"
        assert sensor_msg["mac"] == "FCF5C464BA0E"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 25.55
        assert sensor_msg["humidity"] == 45.81
        assert sensor_msg["tvoc"] == 527
        assert sensor_msg["aqi"] == 3
        assert sensor_msg["co2"] == 934
        assert sensor_msg["rssi"] == 61
