"""The tests for the Jaalee ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestJaalee:
    """Tests for the Jaalee parser"""
    def test_jaalee_jht(self):
        """Test Jaalee parser for Jaalee JHT."""
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
        assert sensor_msg["temperature"] == 34.38
        assert sensor_msg["humidity"] == 34.81
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -39

    def test_jaalee_jht_skipping_ibeacon(self):
        """Test Jaalee parser for Jaalee JHT skipping iBeacon messages (no unique uuid)."""
        data_string = "043e2b020100014b1ecdb4f3d21f0201041bff4c000215ebefd08370a247c89837e7b5634df5257420591acb64d7"
        data = bytes(bytearray.fromhex(data_string))
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Jaalee"
        assert sensor_msg["type"] == "JHT"
        assert sensor_msg["mac"] == "D2F3B4CD1E4B"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 34.38
        assert sensor_msg["humidity"] == 34.81
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -41
        assert tracker_msg is None

    def test_jaalee_jht_api_example(self):
        """Test Jaalee parser for Jaalee JHT based on api example."""
        data_string = "043e2b020100014b1ecdb4f3d21f0201041BFF4C000215EBEFD08370A247C89837E7B5634DF52565823D1ACC64d7"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Jaalee"
        assert sensor_msg["type"] == "JHT"
        assert sensor_msg["mac"] == "D2F3B4CD1E4B"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 24.39
        assert sensor_msg["humidity"] == 23.87
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -41

    def test_jaalee_jht_f51c(self):
        """Test Jaalee parser for Jaalee JHT with UUID F51C."""
        data_string = "043E3F0201000065e6aa4cb0c8330201041BFF4C000215EBEFD08370A247C89837E7B5634DF525632E5535CC6403031CF50F161CF56465E6AA4CB0C801632E5535CC"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Jaalee"
        assert sensor_msg["type"] == "JHT"
        assert sensor_msg["mac"] == "C8B04CAAE665"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 22.8
        assert sensor_msg["humidity"] == 33.28
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -52
