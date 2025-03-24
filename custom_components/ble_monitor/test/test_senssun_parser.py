"""The tests for the Senssun ble_parser."""

import datetime

from ble_monitor.ble_parser import BleParser


class TestSenssun:
    """Tests for the Senssun parser"""

    def test_Senssun_IF_B7(self):
        """Test Senssun parser for IF_B7."""
        data_string = "043E2B0201030033B3C1937A181F020106060949465F423714FF0001020311187A93C1B333021A4500B4A1AB61C5"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Senssun"
        assert sensor_msg["type"] == "Senssun Smart Scale"
        assert sensor_msg["mac"] == "187A93C1B333"
        assert sensor_msg["packet"] == "021a4500b4a1"
        assert sensor_msg["data"]
        assert sensor_msg["weight"] == 67.25
        assert sensor_msg["stabilized"] == 1
        assert sensor_msg["impedance"] == 180
        assert sensor_msg["rssi"] == -59
