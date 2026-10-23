"""The tests for the Eddystone-TLM ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestEddystoneTlm:
    """Tests for the Eddystone-TLM parser"""
    def test_eddystone_tlm(self):
        """Test Eddystone-TLM parser."""
        data_string = "043E2502010301494BEFBEADDE190201060303AAFE1116AAFE20000C6F1E000002006D41DB9AB6D7"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["type"] == "Eddystone-TLM"
        assert sensor_msg["mac"] == "DEADBEEF4B49"
        assert sensor_msg["packet"] == 131181
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 30.0
        assert sensor_msg["voltage"] == 3.183
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -41

    def test_eddystone_tlm_unsupported_readings(self):
        """Test Eddystone-TLM parser with an unsupported battery voltage and temperature."""
        data_string = "043E2502010301494BEFBEADDE190201060303AAFE1116AAFE2000000080000002006D41DB9AB6D7"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["type"] == "Eddystone-TLM"
        assert sensor_msg["mac"] == "DEADBEEF4B49"
        assert sensor_msg["packet"] == 131181
        assert sensor_msg["data"]
        assert "temperature" not in sensor_msg
        assert "voltage" not in sensor_msg
        assert "battery" not in sensor_msg
        assert sensor_msg["rssi"] == -41
