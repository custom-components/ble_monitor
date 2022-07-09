"""The tests for the SensorPush ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestSensorPush:
    """Tests for the SensorPush parser"""
    def test_SensorPush_HTw(self):
        """Test SensorPush HT.w parser."""
        data_string = "043E280201000090F083F134A41C0201061106B00A09ECD79DB893BA42D611000009EF06FF04E9187D39D3"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "SensorPush"
        assert sensor_msg["type"] == "HT.w"
        assert sensor_msg["mac"] == "A434F183F090"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 27.69
        assert sensor_msg["humidity"] == 36.53
        # assert sensor_msg["battery"] == 99
        assert sensor_msg["rssi"] == -45

    def test_SensorPush_HTPxw(self):
        """Test SensorPush HTP.xw parser."""
        data_string = "043E2A02010000252B80F134A41E0201061106B00A09ECD79DB893BA42D611000009EF08FF0089E456BEA6B4B3"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "SensorPush"
        assert sensor_msg["type"] == "HTP.xw"
        assert sensor_msg["mac"] == "A434F1802B25"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 22.66
        assert sensor_msg["humidity"] == 46.07
        assert sensor_msg["pressure"] == 989.65
        # assert sensor_msg["battery"] == 99
        assert sensor_msg["rssi"] == -77
