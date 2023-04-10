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
