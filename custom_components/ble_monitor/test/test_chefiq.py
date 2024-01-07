"""The tests for the Chef iQ ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestChefiQ:
    """Tests for the Chef iQ  parser"""

    def test_chefiq_cq60(self):
        """Test Chef iQ  parser for CQ60 Chef iQ wireless meat thermometer"""
        data_string = "043E250201000073332e3638d91902010615ffcd0501406313c000c900c900ca00cb00c0008d11CC"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Chef iQ"
        assert sensor_msg["type"] == "CQ60"
        assert sensor_msg["mac"] == "D938362E3373"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["meat temperature"] == 20.1
        assert sensor_msg["temperature probe tip"] == 20.1
        assert sensor_msg["temperature probe 1"] == 20.2
        assert sensor_msg["temperature probe 2"] == 20.3
        assert sensor_msg["temperature probe 3"] == 19
        assert sensor_msg["ambient temperature"] == 19.2
        assert sensor_msg["battery"] == 99
        assert sensor_msg["rssi"] == -52
