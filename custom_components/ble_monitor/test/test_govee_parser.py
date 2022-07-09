"""The tests for the Govee ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestGovee:
    """Tests for the Govee parser"""
    def test_Govee_H5051(self):
        """Test Govee H5051 parser."""
        data_string = "043e1902010400aabb615960e30d0cff88ec00ba0af90f63020101b7"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5051/H5071"
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
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

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
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

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
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5072/H5075"
        assert sensor_msg["mac"] == "A4C13861BBAA"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 20.5149
        assert sensor_msg["humidity"] == 14.9
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -86

    def test_Govee_H5075_double(self):
        """Test Govee H5075 parser with BLE advertisement with double manufacturer specific data packet."""
        data_string = "043e4602010000116c2438c1a43a0d09475648353037355f36433131030388ec02010509ff88ec00012d6e64001aff4c000215494e54454c4c495f524f434b535f48575075f2ffc2b3"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5072/H5075"
        assert sensor_msg["mac"] == "A4C138246C11"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 7.7166
        assert sensor_msg["humidity"] == 16.6
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -77

    def test_Govee_H5178_sensor_0(self):
        """Test Govee H5178 parser."""
        data_string = "043E2B0201000045C5DF38C1A41F0A09423531373843353435030388EC0201050CFF010001010003A00F640000BF"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

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
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5178-outdoor"
        assert sensor_msg["mac"] == "A4C138DFC546"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 19.5719
        assert sensor_msg["humidity"] == 71.9
        assert sensor_msg["sensor id"] == 1
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -65

    def test_Govee_H5179(self):
        """Test Govee H5179 parser."""
        data_string = "043E19020104006F18128132E30D0CFF0188EC000101A00AA2175BB6"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5179"
        assert sensor_msg["mac"] == "E3328112186F"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 27.2
        assert sensor_msg["humidity"] == 60.5
        assert sensor_msg["battery"] == 91
        assert sensor_msg["rssi"] == -74

    def test_Govee_H5182(self):
        """Test Govee H5182 parser."""
        data_string = "043e28020100014455303031c71c0201060303518214ff30554401000101e401860834ffff860960ffffcf"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5182"
        assert sensor_msg["mac"] == "C73130305544"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature probe 1"] == 21.0
        assert sensor_msg["temperature alarm probe 1"] == 0.0
        assert sensor_msg["temperature probe 2"] == 24.0
        assert sensor_msg["temperature alarm probe 2"] == 0.0
        assert sensor_msg["rssi"] == -49

    def test_Govee_H5182_alarm(self):
        """Test Govee H5182 parser with alarm."""
        data_string = "043e28020100014455303031c71c0201060303518214ff30554401000101e4018608341cdc8609602249d1"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5182"
        assert sensor_msg["mac"] == "C73130305544"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature probe 1"] == 21.0
        assert sensor_msg["temperature alarm probe 1"] == 73.88
        assert sensor_msg["temperature probe 2"] == 24.0
        assert sensor_msg["temperature alarm probe 2"] == 87.77
        assert sensor_msg["rssi"] == -47

    def test_Govee_H5183(self):
        """Test Govee H5183 parser."""
        data_string = "043e2b02010000edaeac38c1a41f0303518302010511ff5DA1B401000101E400800A2813240000000000000000a9"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5183"
        assert sensor_msg["mac"] == "A4C138ACAEED"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature probe 1"] == 26.0
        assert sensor_msg["temperature alarm probe 1"] == 49.0
        assert sensor_msg["rssi"] == -87

    def test_Govee_H5185(self):
        """Test Govee H5185 parser."""
        data_string = "043e2b020100010a49323633d81f0201060303518517ff32490a01000101e4c1ff0960ffffffff0a28ffffffffc5"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5185"
        assert sensor_msg["mac"] == "D8333632490A"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature probe 1"] == 24.0
        assert sensor_msg["temperature alarm probe 1"] == 0.0
        assert sensor_msg["temperature probe 2"] == 26.0
        assert sensor_msg["temperature alarm probe 2"] == 0.0
        assert sensor_msg["rssi"] == -59

    def test_Govee_H5185_alarm(self):
        """Test Govee H5185 parser with alarm."""
        data_string = "043e2b020100010a49323633d81f0201060303518517ff32490a01000101e4c19609c41bbcffff0a282474ffffca"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Govee"
        assert sensor_msg["type"] == "H5185"
        assert sensor_msg["mac"] == "D8333632490A"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature probe 1"] == 25.0
        assert sensor_msg["temperature alarm probe 1"] == 71.0
        assert sensor_msg["temperature probe 2"] == 26.0
        assert sensor_msg["temperature alarm probe 2"] == 93.32
        assert sensor_msg["rssi"] == -54
