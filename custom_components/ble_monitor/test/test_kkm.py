"""The tests for the KKM ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestKKM:
    """Tests for the KKM parser"""
    def test_kkm_k6(self):
        """Test KKM BLE parser for K6 sensors"""
        data_string = "043E26020100016CD0060234DD1A0201060303AAFE1216AAFE2101070e5b16531f95FFFCFFEC03EBD3"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "KKM"
        assert sensor_msg["type"] == "K6 Sensor Beacon"
        assert sensor_msg["mac"] == "DD340206D06C"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 22.32421875
        assert sensor_msg["humidity"] == 31.58203125
        assert sensor_msg["acceleration"] == 1003.2
        assert sensor_msg["acceleration x"] == -4
        assert sensor_msg["acceleration y"] == -20
        assert sensor_msg["acceleration z"] == 1003
        assert sensor_msg["voltage"] == 3.675
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -45

    def test_kkm_k6_neg_temp(self):
        """Test KKM BLE parser for K6 sensors with negative temperature"""
        data_string = "043E26020100016CD0060234DD1A0201060303AAFE1216AAFE2101070e5bffc01f95FFFCFFEC03EBD3"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "KKM"
        assert sensor_msg["type"] == "K6 Sensor Beacon"
        assert sensor_msg["mac"] == "DD340206D06C"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == -0.25
        assert sensor_msg["humidity"] == 31.58203125
        assert sensor_msg["acceleration"] == 1003.2
        assert sensor_msg["acceleration x"] == -4
        assert sensor_msg["acceleration y"] == -20
        assert sensor_msg["acceleration z"] == 1003
        assert sensor_msg["voltage"] == 3.675
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -45
