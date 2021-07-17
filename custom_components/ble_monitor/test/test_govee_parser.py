"""The tests for the Govee ble_parser."""
import pytest
from ble_monitor.ble_parser import ble_parser


class TestGovee:

    @pytest.fixture(autouse=True)
    def _init_ble_monitor(self):
        self.lpacket_ids = {}
        self.movements_list = {}
        self.adv_priority = {}
        self.trackerlist = []
        self.report_unknown = "other"
        self.discovery = True

    def test_Govee_H5074(self):
        """Test Govee H5074 parser."""
        data_string = "043e1702010400aabb611d12e00b0aff88ec0088078c116402a6"
        data = bytes(bytearray.fromhex(data_string))
        sensor_msg, tracker_msg = ble_parser(self, data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5051/H5074"
        assert sensor_msg["mac"] == "E0121D61BBAA"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 19.28
        assert sensor_msg["humidity"] == 44.92
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -90

    def test_Govee_H5102(self):
        """Test Govee H5102 parser."""
        data_string = "043e2b02010000aabb611d12e11f0d09475648353130325f43423942030388ec02010509ff0100010103cb0164aa"
        data = bytes(bytearray.fromhex(data_string))
        sensor_msg, tracker_msg = ble_parser(self, data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5101/H5102/H5177"
        assert sensor_msg["mac"] == "E1121D61BBAA"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 24.8577
        assert sensor_msg["humidity"] == 57.7
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -86

    def test_Govee_H5075(self):
        """Test Govee H5075 parser."""
        data_string = "043e2b02010000aabb6138c1a41f0d09475648353037355f43423942030388ec02010509ff88ec0003215d6400aa"
        data = bytes(bytearray.fromhex(data_string))
        sensor_msg, tracker_msg = ble_parser(self, data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5072/H5075"
        assert sensor_msg["mac"] == "A4C13861BBAA"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 20.5149
        assert sensor_msg["humidity"] == 14.9
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -86


if __name__ == '__main__':
    unittest.main()