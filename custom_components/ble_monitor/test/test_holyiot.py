"""The tests for the HolyIOT ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestHolyIOT:
    """Tests for the HolyIOT parser"""
    def test_holyiot_temperature(self):
        """Test HolyIOT parser for BLE tracker mini."""
        data_string = "043e49020102018ef1f645b5c63d0201061AFF4C0002159976AED5F58C49AF85EBD0AC7281E3F6271B4CB9240D0962696E2D747261636B657200101642524164C6B545F6F18E060601ED25CC"
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
        assert sensor_msg["temperature"] == -19.37
        assert sensor_msg["rssi"] == -52

    def test_holyiot_pressure(self):
        """Test HolyIOT parser for BLE tracker mini."""
        data_string = "043e49020102018ef1f645b5c63d0201061AFF4C0002159976AED5F58C49AF85EBD0AC7281E3F6271B4CB9240D0962696E2D747261636B657200101642524164C6B545F6F18E0606025334CC"
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
        assert sensor_msg["pressure"] == 101300
        assert sensor_msg["rssi"] == -52

    def test_holyiot_humidity(self):
        """Test HolyIOT parser for BLE tracker mini."""
        data_string = "043e49020102018ef1f645b5c63d0201061AFF4C0002159976AED5F58C49AF85EBD0AC7281E3F6271B4CB9240D0962696E2D747261636B657200101642524164C6B545F6F18E0606034C00CC"
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
        assert sensor_msg["humidity"] == 76
        assert sensor_msg["rssi"] == -52

    def test_holyiot_vibration(self):
        """Test HolyIOT parser for BLE tracker mini."""
        data_string = "043e49020102018ef1f645b5c63d0201061AFF4C0002159976AED5F58C49AF85EBD0AC7281E3F6271B4CB9240D0962696E2D747261636B657200101642524164C6B545F6F18E0606040100CC"
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
        assert sensor_msg["vibration"]
        assert sensor_msg["rssi"] == -52

    def test_holyiot_side(self):
        """Test HolyIOT parser for BLE tracker mini."""
        data_string = "043e49020102018ef1f645b5c63d0201061AFF4C0002159976AED5F58C49AF85EBD0AC7281E3F6271B4CB9240D0962696E2D747261636B657200101642524164C6B545F6F18E0606050500CC"
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
        assert sensor_msg["side"] == 5
        assert sensor_msg["rssi"] == -52

    def test_holyiot_button(self):
        """Test HolyIOT parser for BLE tracker mini."""
        data_string = "043e49020102018ef1f645b5c63d0201061AFF4C0002159976AED5F58C49AF85EBD0AC7281E3F6271B4CB9240D0962696E2D747261636B657200101642524164C6B545F6F18E0606060100CC"
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
        assert sensor_msg["button"] == "toggle"
        assert sensor_msg["rssi"] == -52
