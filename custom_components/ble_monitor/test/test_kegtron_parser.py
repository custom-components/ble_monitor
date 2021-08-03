"""The tests for the kegtron ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestKegtron:

    def test_kegtron_kt100(self):
        """Test kegtron parser for KT-100."""
        data_string = "043e2b02010400759b5c5ecfd01f1effffff49ef138802e20153696e676c6520506f7274000000000000000000ae"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Kegtron"
        assert sensor_msg["type"] == "Kegtron KT-100"
        assert sensor_msg["mac"] == "D0CF5E5C9B75"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["keg size"] == "Corny (5.0 gal)"
        assert sensor_msg["volume start"] == 5.0
        assert sensor_msg["port state"] == "configured"
        assert sensor_msg["port index"] == 1
        assert sensor_msg["port count"] == "Single port device"
        assert sensor_msg["port name"] == "Single Port"
        assert sensor_msg["volume dispensed port 1"] == 0.738
        assert sensor_msg["rssi"] == -82

    def test_kegtron_kt200(self):
        """Test kegtron parser for KT-200."""
        data_string = "043e2b02010400759b5c5ecfd01f1effffff49ef138802e251326e6420506f7274000000000000000000000000af"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Kegtron"
        assert sensor_msg["type"] == "Kegtron KT-200"
        assert sensor_msg["mac"] == "D0CF5E5C9B75"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["keg size"] == "Corny (5.0 gal)"
        assert sensor_msg["volume start"] == 5.0
        assert sensor_msg["port state"] == "configured"
        assert sensor_msg["port index"] == 2
        assert sensor_msg["port count"] == "Dual port device"
        assert sensor_msg["port name"] == "2nd Port"
        assert sensor_msg["volume dispensed port 2"] == 0.738
        assert sensor_msg["rssi"] == -81
