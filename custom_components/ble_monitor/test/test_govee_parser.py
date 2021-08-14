"""The tests for the Govee ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestGovee:
    def test_Govee_H5051(self):
        """Test Govee H5051 parser."""
        data_string = "043e1902010400aabb615960e30d0cff88ec00ba0af90f63020101b7"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5051"
        assert sensor_msg["mac"] == "E3605961BBAA"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 27.46
        assert sensor_msg["humidity"] == 40.89
        assert sensor_msg["battery"] == 99
        assert sensor_msg["rssi"] == -73

    def test_Govee_H5074(self):
        """Test Govee H5074 parser."""
        data_string = "043e1702010400aabb611d12e00b0aff88ec0088078c116402a6"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5074"
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
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

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
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5072/H5075"
        assert sensor_msg["mac"] == "A4C13861BBAA"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 20.5149
        assert sensor_msg["humidity"] == 14.9
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -86

    def test_Govee_H5178_sensor_0(self):
        """Test Govee H5178 parser."""
        data_string = "043E2B0201000045C5DF38C1A41F0A09423531373843353435030388EC0201050CFF010001010003A00F640000BF"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5178"
        assert sensor_msg["mac"] == "A4C138DFC545"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 23.7583
        assert sensor_msg["humidity"] == 58.3
        assert sensor_msg["sensor id"] == 0
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -65

    def test_Govee_H5178_sensor_1(self):
        """Test Govee H5178 parser."""
        data_string = "043E2B0201000045C5DF38C1A41F0A09423531373843353435030388EC0201050CFF010001010102FC87640002BF"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5178"
        assert sensor_msg["mac"] == "A4C138DFC545"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature outdoor"] == 19.5719
        assert sensor_msg["humidity outdoor"] == 71.9
        assert sensor_msg["sensor id"] == 1
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -65

    def test_Govee_H5179(self):
        """Test Govee H5179 parser."""
        data_string = "043E19020104006F18128132E30D0CFF0188EC000101A00AA2175BB6"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5179"
        assert sensor_msg["mac"] == "E3328112186F"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 27.2
        assert sensor_msg["humidity"] == 60.5
        assert sensor_msg["battery"] == 91
        assert sensor_msg["rssi"] == -74
