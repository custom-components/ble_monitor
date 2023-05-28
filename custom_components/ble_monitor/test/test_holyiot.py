"""The tests for the HolyIOT ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestHolyIOT:
    """Tests for the HolyIOT parser"""
    def test_holyiot(self):
        """Test HolyIOT parser for BLE tracker mini."""
        data_string = "043e49020102018ef1f645b5c63d0201061AFF4C0002159976AED5F58C49AF85EBD0AC7281E3F6271B4CB9240D0962696E2D747261636B657200101642524164C6B545F6F18E0606060000CC"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "HolyIOT"
        assert sensor_msg["type"] == "HolyIOT BLE tracker"
        assert sensor_msg["mac"] == "C6B545F6F18E"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["battery"] == 100
        assert not sensor_msg["remote single press"]
        assert sensor_msg["rssi"] == -52
