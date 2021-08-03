"""The tests for the Ruuvitag ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestRuuviTag:

    def test_ruuvitag_v2(self):
        """Test ruuvitag v2 parser."""
        data_string = "043E2A0201030157168974A5F41E0201060303AAFE1616AAFE10EE037275752E76692F23416A7759414D4666CD"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Ruuvitag V2"
        assert sensor_msg["type"] == "Ruuvitag"
        assert sensor_msg["mac"] == "F4A574891657"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 24.0
        assert sensor_msg["humidity"] == 30.0
        assert sensor_msg["pressure"] == 995.03
        assert sensor_msg["rssi"] == -51

    def test_ruuvitag_v3(self):
        """Test ruuvitag v3 parser."""
        data_string = "043E2502010301F27A52FAD4CD1902010415FF990403291A1ECE1EFC18F94202CA0B53000000009E"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Ruuvitag V3"
        assert sensor_msg["type"] == "Ruuvitag"
        assert sensor_msg["mac"] == "CDD4FA527AF2"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 26.3
        assert sensor_msg["humidity"] == 20.5
        assert sensor_msg["pressure"] == 1027.66
        assert sensor_msg["acceleration"] == 2118.6958252660997
        assert sensor_msg["acceleration x"] == -1000
        assert sensor_msg["acceleration y"] == -1726
        assert sensor_msg["acceleration z"] == 714
        assert sensor_msg["voltage"] == 2.899
        assert sensor_msg["battery"] == 89.9
        assert sensor_msg["rssi"] == -98

    def test_ruuvitag_v4(self):
        """Test ruuvitag v4 parser."""
        data_string = "043E2B02010301C4C437D31ED01F0201060303AAFE1716AAFE10F6037275752E76692F2342475159414D71387798"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Ruuvitag V4"
        assert sensor_msg["type"] == "Ruuvitag"
        assert sensor_msg["mac"] == "D01ED337C4C4"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 24.0
        assert sensor_msg["humidity"] == 50.0
        assert sensor_msg["pressure"] == 1019.0
        assert sensor_msg["rssi"] == -104

    def test_ruuvitag_v5(self):
        """Test ruuvitag v5 parser."""
        data_string = "043E2B02010301F27A52FAD4CD1F0201061BFF990405138A5F61C4F0FFE4FFDC0414C5B6EC29B3F27A52FAD4CDBC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Ruuvitag V5"
        assert sensor_msg["type"] == "Ruuvitag"
        assert sensor_msg["mac"] == "CDD4FA527AF2"
        assert sensor_msg["packet"] == 10675
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 25.01
        assert sensor_msg["humidity"] == 61.04
        assert sensor_msg["pressure"] == 1004.16
        assert sensor_msg["acceleration"] == 1044.9956937710317
        assert sensor_msg["acceleration x"] == -28
        assert sensor_msg["acceleration y"] == -36
        assert sensor_msg["acceleration z"] == 1044
        assert sensor_msg["voltage"] == 3.181
        assert sensor_msg["battery"] == 100
        assert sensor_msg["tx power"] == 4
        assert sensor_msg["motion"] == 0
        assert sensor_msg["motion timer"] == 0
        assert sensor_msg["rssi"] == -68
