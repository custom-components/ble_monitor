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

    def test_holyiot_b1_b_battery(self):
        """Test HolyIOT parser for B1-B beacon (real capture)."""
        data_string = "043e49020102016eee4ce590e13d0201061affffff0215fda50693a4e24fb1afcfc6eb07647825271b4cb9c9110942312d420000000000000000000000000c160a1801e190e54cee6e0461b9"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "HolyIOT"
        assert sensor_msg["type"] == "HolyIOT Beacon"
        assert sensor_msg["mac"] == "E190E54CEE6E"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["battery"] == 97
        assert sensor_msg["rssi"] == -71

    def test_holyiot_b1_s_battery(self):
        """Test HolyIOT parser for B1-S beacon (real capture)."""
        data_string = "043e4902010201bd483e2817fb3d0201061affffff0215fda50693a4e24fb1afcfc6eb07647825271b4cb9c9110942312d530000000000000000000000000c160a1801fb17283e48bd0462b9"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "HolyIOT"
        assert sensor_msg["type"] == "HolyIOT Beacon"
        assert sensor_msg["mac"] == "FB17283E48BD"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["battery"] == 98
        assert sensor_msg["rssi"] == -71

    def test_holyiot_beacon_ibeacon_mode(self):
        """Test HolyIOT parser for the iBeacon-mode frame (type byte 0x02, real capture)."""
        data_string = "043e49020102016eee4ce590e13d0201061affffff02156b1e44d99f274c8eb3f10a5d82e49c7300010001c9110942312d420000000000000000000000000c160a1802e190e54cee6ef85fb0"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "HolyIOT"
        assert sensor_msg["type"] == "HolyIOT Beacon"
        assert sensor_msg["mac"] == "E190E54CEE6E"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["battery"] == 95
        assert sensor_msg["rssi"] == -80

    def test_holyiot_b1_mac_mismatch(self):
        """Test HolyIOT parser drops B1 frames with a foreign MAC in payload."""
        data_string = "043e49020102016eee4ce590e13d0201061affffff0215fda50693a4e24fb1afcfc6eb07647825271b4cb9c9110942312d420000000000000000000000000c160a1801e090e54cee6e0461b9"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg is None
