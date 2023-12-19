"""The tests for the Grundfos ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestGrundfos:
    """Tests for the Grundfos parser"""
    def test_grundfos_MI401(self):
        """Test Grundfos parser for ALPHA reader MI401."""
        data_string = "043E2A020103009565F1164DAC1E06084D4934303116FF14F230017A03059884103E0F19070D0114FFFFFFFFC0"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Grundfos"
        assert sensor_msg["type"] == "MI401"
        assert sensor_msg["mac"] == "AC4D16F16595"
        assert sensor_msg["packet"] == 122
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 13
        assert sensor_msg["flow"] == 645.2
        assert sensor_msg["water pressure"] == 0.119
        assert sensor_msg["pump mode"] == "Constant differential pressure level 1"
        assert sensor_msg["pump id"] == 38917
        assert sensor_msg["battery status"] == 3
        assert sensor_msg["rssi"] == -64
