"""The tests for the Sonoff ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestSonoff:
    """Tests for the HHCC parser"""
    def test_sonoff_s_mate(self):
        """Test Sonoff BLE parser for S-MATE"""
        data_string = "043e2b020103011122334455661f0201021b05ffffee1bc878f64a4690dd5ad9e71f4e4177f011694babb7fe68ba"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Sonoff"
        assert sensor_msg["type"] == "S-MATE"
        assert sensor_msg["mac"] == "00005AD9E71F"
        assert sensor_msg["packet"] == 91
        assert sensor_msg["data"]
        assert sensor_msg["three btn switch left"] == "toggle"
        assert sensor_msg["button switch"] == "single press"
        assert sensor_msg["rssi"] == -70

    def test_sonoff_r5(self):
        """Test Sonoff BLE parser for R5"""
        data_string = "043e2b020103011122334455661f0201021B05FFFFEE1BC878F64A4790365AD509227B7442C5245C7DE4828B98ae"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Sonoff"
        assert sensor_msg["type"] == "R5"
        assert sensor_msg["mac"] == "00005AD50922"
        assert sensor_msg["packet"] == 801
        assert sensor_msg["data"]
        assert sensor_msg["six btn switch top left"] == "toggle"
        assert sensor_msg["button switch"] == "single press"
        assert sensor_msg["rssi"] == -82
