"""The tests for the Teltonika ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestTeltonika:
    """Tests for the Teltonica parser"""
    def test_blue_puck_T(self):
        """Test Teltonika parser for Blue Puck T."""
        data_string = "043e1e02010001e7e193546ec61202010605166e2a860b08095055434b5f5431dd"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Teltonika"
        assert sensor_msg["type"] == "Blue Puck T"
        assert sensor_msg["mac"] == "C66E5493E1E7"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 29.5
        assert sensor_msg["rssi"] == -35

    def test_blue_coin_T(self):
        """Test Teltonika parser for Blue Coin T."""
        data_string = "043e210201000196826a022bf01502010605166e2ad0090b0943205420383031424239d1"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Teltonika"
        assert sensor_msg["type"] == "Blue Coin T"
        assert sensor_msg["mac"] == "F02B026A8296"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 25.12
        assert sensor_msg["rssi"] == -47

    def test_blue_puck_RHT(self):
        """Test Teltonika parser for Blue Puck RHT."""
        data_string = "043e230201000196826a022bf01702010605166e2aa30404166f2a2308095055434b5f5448bd"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Teltonika"
        assert sensor_msg["type"] == "Blue Puck RHT"
        assert sensor_msg["mac"] == "F02B026A8296"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 11.87
        assert sensor_msg["humidity"] == 35
        assert sensor_msg["rssi"] == -67

    def test_ela_blue_puck_T(self):
        """Test Teltonika parser for Ela Blue Puck T (rebrand of Teltonika)."""
        data_string = "043e2502010001f925c2f1e9ff1902010606ff5707122e070e0950205420454E20383039303646dd"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Teltonika"
        assert sensor_msg["type"] == "Blue Puck T"
        assert sensor_msg["mac"] == "FFE9F1C225F9"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 18.38
        assert sensor_msg["rssi"] == -35

    def test_ela_blue_puck_RHT(self):
        """Test Teltonika parser for Ela Blue Puck RHT (rebrand of Teltonika)."""
        data_string = "043e2602010001f925c2f1e9ff1a02010608ff5707213012b80a0d09502052485420393030343539dd"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Teltonika"
        assert sensor_msg["type"] == "Blue Puck RHT"
        assert sensor_msg["mac"] == "FFE9F1C225F9"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 27.44
        assert sensor_msg["humidity"] == 48
        assert sensor_msg["rssi"] == -35

    def test_ela_blue_puck_T_with_batt(self):
        """Test Teltonika parser for Ela Blue Puck T with battery (rebrand of Teltonika)."""
        data_string = "043e2b02010001f925c2f1e9ff1f02010606ff570712980a0e0950205420454E2038303930364605ff5707f10ddd"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Teltonika"
        assert sensor_msg["type"] == "Blue Puck T"
        assert sensor_msg["mac"] == "FFE9F1C225F9"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 27.12
        assert sensor_msg["battery"] == 13
        assert sensor_msg["rssi"] == -35
