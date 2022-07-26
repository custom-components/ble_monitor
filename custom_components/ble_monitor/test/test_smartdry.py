"""The tests for the SmartDry ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestSmartDry:
    """Tests for the SmartDry parser"""
    def test_cloth_dryer(self):
        """Test SmartDry parser for cloth dryer ."""
        data_string = "043e3902010000ad114bdc1b002d02010607093241485a44560fffae017de6ea41702360420000c406020a031107fb349b5f8000008000100000aac7"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "SmartDry"
        assert sensor_msg["type"] == "SmartDry cloth dryer"
        assert sensor_msg["mac"] == "001BDC4B11AD"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 29.3625431060791
        assert sensor_msg["humidity"] == 56.03460693359375
        assert sensor_msg["voltage"] == 1.732
        assert sensor_msg["battery"] == 0
        assert sensor_msg["switch"]
        assert sensor_msg["rssi"] == -57
