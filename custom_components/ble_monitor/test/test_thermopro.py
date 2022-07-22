"""The tests for the Thermopro ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestThermoro:
    """Tests for the Thermopro parser"""

    def test_thermopro_tp357(self):
        """Test Thermopro TP357 parser."""
        data_string = "043e2502010000012a98487e48190d0954503335372028324130312902010507ffc2170127022cbc"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Thermopro"
        assert sensor_msg["type"] == "TP357"
        assert sensor_msg["mac"] == "487E48982A01"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 27.9
        assert sensor_msg["humidity"] == 39
        assert sensor_msg["rssi"] == -68

    def test_thermopro_tp359(self):
        """Test Thermopro TP359 parser."""
        data_string = "043e330d01130000870cf2487e480100ff7fd8000000000000000000190d0954503335392028304338372902010507ffc2ff0035012c"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Thermopro"
        assert sensor_msg["type"] == "TP359"
        assert sensor_msg["mac"] == "487E48F20C87"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 25.5
        assert sensor_msg["humidity"] == 53
        assert sensor_msg["rssi"] == -40
