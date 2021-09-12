"""The tests for the Moat ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestMoat:
    def test_Moat_S2(self):
        """Test Moat S2 parser."""
        data_string = "043e3702010000aabb611d12e12b0d09475648353130325f43423942030388ec02010515ff0010AABBCCDDEEFF11111111d46103cbbe0a0000aa"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Moat"
        assert sensor_msg["type"] == "Moat S2"
        assert sensor_msg["mac"] == "E1121D61BBAA"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 20.300
        assert sensor_msg["humidity"] == 93.127
        assert sensor_msg["battery"] == 19.5
        assert sensor_msg["rssi"] == -86
