"""The tests for the Minew ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestMinew:
    """Tests for the Minew E9 parser.

    Frames are taken from the reelyActive advlib-ble-services unit tests.
    """
    def test_minew_e9(self):
        """Test Minew E9 temperature frame parser."""
        data_string = "043E2202010301AABBCCDDEEFF160201060303E1FF0E16E1FFA113631973AABBCCDDEEFFC4"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Minew"
        assert sensor_msg["type"] == "E9"
        assert sensor_msg["mac"] == "FFEEDDCCBBAA"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 25.45
        assert sensor_msg["battery"] == 99
        assert sensor_msg["rssi"] == -60

    def test_minew_e9_negative_temperature(self):
        """Test Minew E9 temperature frame parser below 0 °C."""
        data_string = "043E2202010301AABBCCDDEEFF160201060303E1FF0E16E1FFA11363FB80AABBCCDDEEFFC4"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["type"] == "E9"
        assert sensor_msg["temperature"] == -4.5

    def test_minew_other_frame_ignored(self):
        """Test that other Minew frames of the same length (here TVOC) are not parsed."""
        data_string = "043E2202010301AABBCCDDEEFF160201060303E1FF0E16E1FFA112634000AABBCCDDEEFFC4"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg is None
