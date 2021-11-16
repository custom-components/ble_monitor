"""The tests for the iNode ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestInode:
    """Tests for the iNode parser"""
    def test_inode_energy_meter(self):
        """Test inode parser for iNode Energy Monitor."""
        data_string = "043E2102010000473A6D6F1200150201060EFF90820400CFE40000DC05B0ED10020A08A5"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "iNode"
        assert sensor_msg["type"] == "iNode Energy Meter"
        assert sensor_msg["mac"] == "00126F6D3A47"
        assert sensor_msg["packet"] == "0400cfe40000dc05b0ed10"
        assert sensor_msg["data"]
        assert sensor_msg["energy"] == 39.05
        assert sensor_msg["energy unit"] == "kWh"
        assert sensor_msg["power"] == 160.0
        assert sensor_msg["power unit"] == "W"
        assert sensor_msg["constant"] == 1500
        assert sensor_msg["battery"] == 100
        assert sensor_msg["voltage"] == 2.88
        assert sensor_msg["light level"] == 0.0
        assert sensor_msg["week day"] == 0
        assert sensor_msg["week day total"] == 4333
        assert sensor_msg["rssi"] == -91

    def test_inode_care_sensor_1(self):
        """Test inode parser for iNode Care Sensor 1."""
        data_string = "043e290201000070ec4318f0d01d02010619ff929101b000001700a81900000400f4bbce6e77a00b97d1b5c5"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "iNode"
        assert sensor_msg["type"] == "iNode Care Sensor 1"
        assert sensor_msg["mac"] == "D0F01843EC70"
        assert sensor_msg["packet"] == "01b000001700a81900000400f4bbce6e77a00b97d1b5"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == -30
        assert sensor_msg["motion"] == 0
        assert sensor_msg["acceleration"] == 9.0
        assert sensor_msg["acceleration x"] == 0
        assert sensor_msg["acceleration y"] == 0
        assert sensor_msg["acceleration z"] == -9
        assert sensor_msg["battery"] == 100
        assert sensor_msg["voltage"] == 2.88
        assert sensor_msg["rssi"] == -59

    def test_inode_care_sensor_ht(self):
        """Test inode parser for iNode Care Sensor HT."""
        data_string = "043e290201000071ec4318f0d01d02010619ff909b01a0000000007f14b9298e61af6cde99ef797870ee41c5"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "iNode"
        assert sensor_msg["type"] == "iNode Care Sensor HT"
        assert sensor_msg["mac"] == "D0F01843EC71"
        assert sensor_msg["packet"] == "01a0000000007f14b9298e61af6cde99ef797870ee41"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 9.424587402343747
        assert sensor_msg["humidity"] == 75.48956298828125
        assert sensor_msg["battery"] == 90
        assert sensor_msg["voltage"] == 2.76
        assert sensor_msg["rssi"] == -59
