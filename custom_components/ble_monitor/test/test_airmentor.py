"""The tests for the Air Mentor ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestSwitchbot:
    """Tests for the Air Mentor parser"""
    def test_air_mentor_pro_2_set_1(self):
        """Test Air Mentor parser for Air Mentor Pro 2."""
        data_string = "043E1B02010000A7808FE648540F0201060BFF222100b91963332d0145CC"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Air Mentor"
        assert sensor_msg["type"] == "Air Mentor Pro 2"
        assert sensor_msg["mac"] == "5448E68F80A7"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 24.99
        assert sensor_msg["temperature calibrated"] == 19.89
        assert sensor_msg["humidity"] == 61.34
        assert sensor_msg["tvoc"] == 185
        assert sensor_msg["aqi"] == 325
        assert sensor_msg["air quality"] == "hazardous"
        assert sensor_msg["rssi"] == -52

    def test_air_mentor_pro_2_set_2(self):
        """Test Air Mentor parser for Air Mentor Pro 2."""
        data_string = "043E1B02010000A7808FE648540F0201060BFF21212710000300030000CC"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Air Mentor"
        assert sensor_msg["type"] == "Air Mentor Pro 2"
        assert sensor_msg["mac"] == "5448E68F80A7"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["co2"] == 10000
        assert sensor_msg["pm2.5"] == 3
        assert sensor_msg["pm10"] == 3
        assert sensor_msg["rssi"] == -52
