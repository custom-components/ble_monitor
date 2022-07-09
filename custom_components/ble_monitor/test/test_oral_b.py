"""The tests for the Oral-B ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestOralB:
    """Tests for the Oral-B parser"""
    def test_oral_b_smartseries_7000(self):
        """Test Oral-B parser for Oral-B SmartSeries 7000."""
        data_string = "043e1e020100007173b66a1ba8120201050effdc0003210b0328041107373804b7"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)
        print(sensor_msg)
        assert sensor_msg["firmware"] == "Oral-B"
        assert sensor_msg["type"] == "SmartSeries 7000"
        assert sensor_msg["mac"] == "A81B6AB67371"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["toothbrush"] == 1
        assert sensor_msg["toothbrush state"] == 'running'
        assert sensor_msg["pressure"] == 'unknown pressure 40'
        assert sensor_msg["counter"] == 1041
        assert sensor_msg["mode"] == 'turbo'
        assert sensor_msg["sector"] == 'sector 55'
        assert sensor_msg["sector timer"] == 56
        assert sensor_msg["number of sectors"] == 4
        assert sensor_msg["rssi"] == -73
