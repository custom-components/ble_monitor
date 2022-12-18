"""The tests for the Amazfit ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestAmazfit:
    """Tests for the Amazfit parser"""
    def test_amazfit_smart_scale(self):
        """Test acconeer parser for Amazfit Smart Scale."""
        data_string = "043e390d011300000ea4309e87700100ff7fb10000000000000000001f0201050302e0fe1716e0feba82e6c7fc3414a442bf46ec68000462bba30100"

        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Amazfit"
        assert sensor_msg["type"] == "Amazfit Smart Scale"
        assert sensor_msg["mac"] == "70879E30A40E"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["weight"] == 85.3
        assert sensor_msg["stabilized"] == 1
        assert sensor_msg["non-stabilized weight"] == 85.3
        assert sensor_msg["impedance"] == 517.2
        assert sensor_msg["pulse"] == 104
        assert sensor_msg["rssi"] == -79
