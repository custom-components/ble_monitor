"""The tests for the HA BLE (DIY sensor) ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestHaBle:
    """Tests for the HA BLE (DIY sensor) parser"""
    def test_ha_ble_battery(self):
        """Test HA BLE parser for battery measurement"""
        data_string = "043e1c02010000a5808fe6485410020106070848415f424c450416192a59cc"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["battery"] == 89
        assert sensor_msg["rssi"] == -52

    def test_ha_ble_temperature(self):
        """Test HA BLE parser for temperature measurement"""
        data_string = "043E1D02010000A5808FE6485411020106070848415F424C4505166E2A3409CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 23.56
        assert sensor_msg["rssi"] == -52

    def test_ha_ble_illuminance(self):
        """Test HA BLE parser for illuminance measurement"""
        data_string = "043E1E02010000A5808FE6485412020106070848415F424C450616FB2A34AA00CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["illuminance"] == 435.72
        assert sensor_msg["rssi"] == -52

    def test_ha_ble_pm25(self):
        """Test HA BLE parser for PM2.5 measurement"""
        data_string = "043E1D02010000A5808FE6485411020106070848415F424C450516D62BAA00BC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["pm2.5"] == 170
        assert sensor_msg["rssi"] == -68

    def test_ha_ble_pm10(self):
        """Test HA BLE parser for PM10 measurement"""
        data_string = "043E1D02010000A5808FE6485411020106070848415F424C450516D72BAB01CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["pm10"] == 427
        assert sensor_msg["rssi"] == -52
