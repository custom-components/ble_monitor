"""The tests for the KKM ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestKKM:
    """Tests for the KKM parser"""
    def test_kkm_k6(self):
        """Test KKM BLE parser for K6 sensors"""
        data_string = "043E26020100016CD0060234DD1A0201060303AAFE1216AAFE21010F0E07192A224FFFFCFFEC03EBD3"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "KKM"
        assert sensor_msg["type"] == "K6 Sensor Beacon"
        assert sensor_msg["mac"] == "DD340206D06C"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 25.42
        assert sensor_msg["humidity"] == 34.79
        assert sensor_msg["acceleration"] == 1003.2
        assert sensor_msg["acceleration x"] == -4
        assert sensor_msg["acceleration y"] == -20
        assert sensor_msg["acceleration z"] == 1003
        assert sensor_msg["voltage"] == 3.591
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -45
