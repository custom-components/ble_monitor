"""The tests for the Relsib ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestRelsib:
    """Tests for the Relsib parser"""
    def test_relsib_AA20(self):
        """Test Relsib parser for AA20 packet type."""
        data_string = "043e2b0201030130ddf27cb6fa1f040945436f191620aa84000000b20a200a15030080f04700c2eb0b010b0300c2"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Relsib (EClerk Eco v9a)"
        assert sensor_msg["type"] == "EClerk Eco"
        assert sensor_msg["mac"] == "FAB67CF2DD30"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 27.38
        assert sensor_msg["humidity"] == 25.92
        assert sensor_msg["co2"] == 789
        assert sensor_msg["battery"] == 71
        assert sensor_msg["rssi"] == -62

    def test_relsib_AA21(self):
        """Test Relsib parser for AA20 packet type."""
        data_string = "043e2b0201030130ddf27cb6fa1f040945436f191621aa220a75094303008045636c65726b45636f0000000000b6"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Relsib (EClerk Eco v9a)"
        assert sensor_msg["type"] == "EClerk Eco"
        assert sensor_msg["mac"] == "FAB67CF2DD30"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 25.94
        assert sensor_msg["humidity"] == 24.21
        assert sensor_msg["co2"] == 835
        assert sensor_msg["rssi"] == -74

    def test_relsib_AA22(self):
        """Test Relsib parser for AA20 packet type."""
        data_string = "043e2b0201030130ddf27cb6fa1f040945436f191622aa210a7509430300804f4f4f2052656c73696200000000bd"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Relsib (EClerk Eco v9a)"
        assert sensor_msg["type"] == "EClerk Eco"
        assert sensor_msg["mac"] == "FAB67CF2DD30"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 25.93
        assert sensor_msg["humidity"] == 24.21
        assert sensor_msg["co2"] == 835
        assert sensor_msg["rssi"] == -67

    def test_relsib_no_data(self):
        """Test Relsib parser for AA20 packet type during device startup when sensors are not ready yet."""
        data_string = "043e2b0201030130ddf27cb6fa1f040945436f191620aa040000000080008000800080f04600c2eb0b010b0300be"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Relsib (EClerk Eco v9a)"
        assert sensor_msg["type"] == "EClerk Eco"
        assert sensor_msg["mac"] == "FAB67CF2DD30"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert "temperature" not in sensor_msg
        assert "humidity" not in sensor_msg
        assert "co2" not in sensor_msg
        assert sensor_msg["rssi"] == -66

    def test_relsib_power_adapter_plugged(self):
        """Test Relsib parser for AA20 packet type while using power adapter instead of battery."""
        data_string = "043e2b0201030130ddf27cb6fa1f040945436f191620aa24080000200a750943030080f08000c2eb0b010b0300b6"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Relsib (EClerk Eco v9a)"
        assert sensor_msg["type"] == "EClerk Eco"
        assert sensor_msg["mac"] == "FAB67CF2DD30"
        assert sensor_msg["battery"] == 100
