"""The tests for the HHCC ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestHHCC:
    """Tests for the HHCC parser"""
    def test_hhcc_HHCCJCY10(self):
        """Test HHCC BLE parser for HHCCJCY10"""
        data_string = "043e2002010001c211e44d23dc14020106030250fd0c1650fd0e006e0134a428005bae"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "HHCC"
        assert sensor_msg["type"] == "HHCCJCY10"
        assert sensor_msg["mac"] == "DC234DE411C2"
        assert sensor_msg["packet"] == "0e006e0134a428005b"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 11.0
        assert sensor_msg["moisture"] == 14
        assert sensor_msg["illuminance"] == 79012
        assert sensor_msg["conductivity"] == 91
        assert sensor_msg["battery"] == 40
        assert sensor_msg["rssi"] == -82
