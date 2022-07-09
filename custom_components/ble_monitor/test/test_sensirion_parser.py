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
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Sensirion"
        assert sensor_msg["type"] == "MyCO2"
        assert sensor_msg["mac"] == "F8EADC3C6735"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 25.63
        assert sensor_msg["humidity"] == 36.16
        assert sensor_msg["co2"] == 1035
        assert sensor_msg["rssi"] == -80

    def test_Sensorion_SHT4x(self):
        """Test Sensirion SHT4x parser."""
        data_string = "043e2902010001e7e2c3c067ff1d0201060bffd5060006e2e7036a1c650d09534854343020476164676574b9"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Sensirion"
        assert sensor_msg["type"] == "SHT40 Gadget"
        assert sensor_msg["mac"] == "FF67C0C3E2E7"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 27.47
        assert sensor_msg["humidity"] == 39.5
        assert sensor_msg["rssi"] == -71
