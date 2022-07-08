"""The tests for the Xiaogui ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestXiaogui:
    """Tests for the Xiaogui parser"""
    def test_xiaogui_tzc4_stab(self):
        """Test Xiaogui parser for Xiaogui TZC4 (stabilized weight)."""
        data_string = "043e1d0201030094e0e5295a5f1110ffc0a30276138b0002215f5a29e5e094bd"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaogui"
        assert sensor_msg["type"] == "TZC4"
        assert sensor_msg["mac"] == "5F5A29E5E094"
        assert sensor_msg["packet"] == 41761
        assert sensor_msg["data"]
        assert sensor_msg["non-stabilized weight"] == 63.0
        assert sensor_msg["weight"] == 63.0
        assert sensor_msg["impedance"] == 500.3
        assert sensor_msg["stabilized"] == 1
        assert sensor_msg["rssi"] == -67

    def test_xiaogui_tzc4_non_stab(self):
        """Test Xiaogui parser for Xiaogui TZC4 (not stabilized weight)."""
        data_string = "043e1d0201030094e0e5295a5f1110ffc05d008c00000002205f5a29e5e094bf"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaogui"
        assert sensor_msg["type"] == "TZC4"
        assert sensor_msg["mac"] == "5F5A29E5E094"
        assert sensor_msg["packet"] == 23840
        assert sensor_msg["data"]
        assert sensor_msg["non-stabilized weight"] == 14.0
        assert "weight" not in sensor_msg
        assert "impedance" not in sensor_msg
        assert sensor_msg["stabilized"] == 0
        assert sensor_msg["rssi"] == -65

    def test_xiaogui_maxxmee_qjj_stab(self):
        """Test Xiaogui parser for MaxxMee Mod QJ-J (stabilized weight)."""
        data_string = "043e1d0201030094e0e5295a5f1110ffc07d2c4700000a01255f5a29e5e094bd"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaogui"
        assert sensor_msg["type"] == "QJ-J"
        assert sensor_msg["mac"] == "5F5A29E5E094"
        assert sensor_msg["packet"] == 32037
        assert sensor_msg["data"]
        assert sensor_msg["non-stabilized weight"] == 113.35
        assert sensor_msg["weight"] == 113.35
        assert sensor_msg["stabilized"] == 1
        assert sensor_msg["rssi"] == -67

    def test_xiaogui_maxxmee_qjj_non_stab(self):
        """Test Xiaogui parser for MaxxMee Mod QJ-J (not stabilized weight)."""
        data_string = "043e1d0201030094e0e5295a5f1110ffc024000000000a01245f5a29e5e094bd"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaogui"
        assert sensor_msg["type"] == "QJ-J"
        assert sensor_msg["mac"] == "5F5A29E5E094"
        assert sensor_msg["packet"] == 9252
        assert sensor_msg["data"]
        assert sensor_msg["non-stabilized weight"] == 0.0
        assert "weight" not in sensor_msg
        assert "impedance" not in sensor_msg
        assert sensor_msg["stabilized"] == 0
        assert sensor_msg["rssi"] == -67
