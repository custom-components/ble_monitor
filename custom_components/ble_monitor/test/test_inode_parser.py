"""The tests for the iNode ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestInode:

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
