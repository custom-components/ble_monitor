"""The tests for the Sensirion ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestSensirion:
    """Tests for the Sensirion parser"""
    def test_Sensorion_MyCO2(self):
        """Test Sensirion MyCO2 parser."""
        data_string = "043e320d0113000135673cdceaf80100ff7fb0000000000000000000180201060dffd506000867355367925c0b0406094d79434f32"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Sensirion"
        assert sensor_msg["type"] == "MyCO2"
        assert sensor_msg["mac"] == "F8:EA:DC:3C:67:35"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"] == True
        assert sensor_msg["temperature"] == 25.63
        assert sensor_msg["humidity"] == 36.16
        assert sensor_msg["co2"] == 1035
        assert sensor_msg["rssi"] == -80

