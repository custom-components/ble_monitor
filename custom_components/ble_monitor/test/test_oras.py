"""The tests for the Oras ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestOras:
    """Tests for the Oras parser"""
    def test_oras_faucet(self):
        """Test Oras parser for Electra Washbin Faucet."""
        data_string = "043e2b02010201da060f38c1a41f02010605094F52415315FF3101006400323131313030373933350020202020CC"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Oras"
        assert sensor_msg["type"] == "Electra Washbasin Faucet"
        assert sensor_msg["mac"] == "A4C1380F06DA"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -52

    def test_garnet_battery(self):
        """Test Oras parser for Garnet 709BT battery sensor."""
        data_string = "043E2102010000adb9a538c1a41502010611ff31010c464e0d31333230303030303030CC"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Garnet"
        assert sensor_msg["type"] == "SeeLevel II 709-BTP3"
        assert sensor_msg["mac"] == "A4C138A5B9AD"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["voltage"] == 13.2
        assert sensor_msg["problem"] == 0
        assert sensor_msg["rssi"] == -52

    def test_garnet_black_tank(self):
        """Test Oras parser for Garnet 709BT black tank sensor."""
        data_string = "043E2102010000adb9a538c1a41502010611ff31010c464e0120373130303030303030CC"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Garnet"
        assert sensor_msg["type"] == "SeeLevel II 709-BTP3"
        assert sensor_msg["mac"] == "A4C138A5B9AD"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["black tank"] == 71
        assert sensor_msg["problem"] == 0
        assert sensor_msg["rssi"] == -52
