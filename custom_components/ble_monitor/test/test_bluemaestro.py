"""The tests for the BlueMaestro ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestBlueMaestro:
    """Tests for the BlueMaestro parser"""
    def test_BlueMaestro_THD(self):
        """Test BlueMaestro Tempo Disc THD parser."""
        data_string = "043e4702010400aabb611d12e03b11ff330117550e10061eff2f02a6ff0301000908111111111111111100000000330174536166650000000000000000616974536166650000000000a6"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BlueMaestro"
        assert sensor_msg["type"] == "Tempo Disc THD"
        assert sensor_msg["mac"] == "E0121D61BBAA"
        assert sensor_msg["packet"] == 1566
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == -20.9
        assert sensor_msg["humidity"] == 67.8
        assert sensor_msg['dewpoint'] == -25.3
        assert sensor_msg["battery"] == 85
        assert sensor_msg["rssi"] == -90
