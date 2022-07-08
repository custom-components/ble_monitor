"""The tests for the Laica Smart Scale ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestLaica:
    """Tests for the Mikrotik parser"""
    def test_mikrotik_tg_bt5_in(self):
        """Test Mikrotik TG-BT5-IN parser."""
        data_string = "043E2202010300DD7B146E2CDC1615FF4F09010010A90000FDFF010000806BE866000062D5"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Mikrotik"
        assert sensor_msg["type"] == "TG-BT5-IN"
        assert sensor_msg["mac"] == "DC2C6E147BDD"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["version"] == 1
        assert sensor_msg["acceleration x"] == 0.0
        assert sensor_msg["acceleration y"] == 255.98828125
        assert sensor_msg["acceleration z"] == 0.00390625
        assert sensor_msg["acceleration"] == 255.9882812798037
        assert sensor_msg["uptime"] == 6744171
        assert sensor_msg["battery"] == 98
        assert sensor_msg["switch"] == 0
        assert sensor_msg["tilt"] == 0
        assert sensor_msg["dropping"] == 0
        assert sensor_msg["impact"] == 0
        assert sensor_msg["impact x"] == 0
        assert sensor_msg["impact y"] == 0
        assert sensor_msg["impact z"] == 0
        assert sensor_msg["rssi"] == -43

    def test_mikrotik_tg_bt5_out(self):
        """Test Mikrotik TG-BT5-OUT parser."""
        data_string = "043E2202010300DD7B146E2CDC1615FF4F09010010A90000FDFF0100A1196BE866000062D5"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Mikrotik"
        assert sensor_msg["type"] == "TG-BT5-OUT"
        assert sensor_msg["mac"] == "DC2C6E147BDD"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg['temperature'] == 25.62890625
        assert sensor_msg["version"] == 1
        assert sensor_msg["acceleration x"] == 0.0
        assert sensor_msg["acceleration y"] == 255.98828125
        assert sensor_msg["acceleration z"] == 0.00390625
        assert sensor_msg["acceleration"] == 255.9882812798037
        assert sensor_msg["uptime"] == 6744171
        assert sensor_msg["battery"] == 98
        assert sensor_msg["switch"] == 0
        assert sensor_msg["tilt"] == 0
        assert sensor_msg["dropping"] == 0
        assert sensor_msg["impact"] == 0
        assert sensor_msg["impact x"] == 0
        assert sensor_msg["impact y"] == 0
        assert sensor_msg["impact z"] == 0
        assert sensor_msg["rssi"] == -43
