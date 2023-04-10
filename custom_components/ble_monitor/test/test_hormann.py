"""The tests for the Hörmann ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestHormann:
    """Tests for the Hörmann parser"""
    def test_hormann_closed(self):
        """Test Air Mentor parser for Hörmann Supramatic E4 BS (closed)."""
        data_string = "043e4002010201da060f38c1a4340201061107B3585540506011E38F96080001909A6609FFB40701022D20000014FFB407140000000000000000efbbafa9d1a73b04CC"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Hörmann"
        assert sensor_msg["type"] == "Supramatic E4 BS"
        assert sensor_msg["mac"] == "A4C1380F06DA"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["opening"] == 0
        assert sensor_msg["opening percentage"] == 0.0
        assert sensor_msg["rssi"] == -52

    def test_hormann_partially_open(self):
        """Test Air Mentor parser for Hörmann Supramatic E4 BS (31% open)."""
        data_string = "043e4002010201da060f38c1a4340201061107B3585540506011E38F96080001909A6609FFB40701022D20000014FFB407173E000000000000006722D81075F42A04CC"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Hörmann"
        assert sensor_msg["type"] == "Supramatic E4 BS"
        assert sensor_msg["mac"] == "A4C1380F06DA"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["opening"] == 1
        assert sensor_msg["opening percentage"] == 31.0
        assert sensor_msg["rssi"] == -52

    def test_hormann_fully_open(self):
        """Test Air Mentor parser for Hörmann Supramatic E4 BS (100% open)."""
        data_string = "043e4002010201da060f38c1a4340201061107B3585540506011E38F96080001909A6609FFB40701022D20000014FFB40713C8000000000000006722D81075F42A04CC"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Hörmann"
        assert sensor_msg["type"] == "Supramatic E4 BS"
        assert sensor_msg["mac"] == "A4C1380F06DA"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["opening"] == 1
        assert sensor_msg["opening percentage"] == 100.0
        assert sensor_msg["rssi"] == -52
