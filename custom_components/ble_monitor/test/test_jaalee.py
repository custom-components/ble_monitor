"""The tests for the Jaalee ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestJaalee:
    """Tests for the Jaalee parser"""
    def test_jaalee_jht(self):
        """Test Tilt parser for Jaalee JHT."""
        data_string = "043e22020104014b1ecdb4f3d216020a00030325f50e1625f5644b1ecdb4f3d27420591ad9"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Jaalee"
        assert sensor_msg["type"] == "JHT"
        assert sensor_msg["mac"] == "D2F3B4CD1E4B"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 32.86
        assert sensor_msg["humidity"] == 37.51
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -39

    def test_jaalee_jht_skipping_ibeacon(self):
        """Test Tilt parser for Jaalee JHT skipping iBeacon messages (no unique uuid)."""
        data_string = "043e2b020100014b1ecdb4f3d21f0201041bff4c000215ebefd08370a247c89837e7b5634df5257420591acb64d7"
        data = bytes(bytearray.fromhex(data_string))
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Jaalee"
        assert sensor_msg["type"] == "JHT"
        assert sensor_msg["mac"] == "D2F3B4CD1E4B"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 32.86
        assert sensor_msg["humidity"] == 37.51
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -41
        assert tracker_msg is None
