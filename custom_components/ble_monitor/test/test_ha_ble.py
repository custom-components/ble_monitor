"""The tests for the HA BLE (DIY sensor) ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestHaBle:
    """Tests for the HA BLE (DIY sensor) parser"""
    def test_ha_ble_packet_and_battery(self):
        """Test HA BLE parser for battery measurement and packet number"""
        data_string = "043E1902010000A5808FE648540D02010609161C18020009020161CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == 9
        assert sensor_msg["data"]
        assert sensor_msg["battery"] == 97
        assert sensor_msg["rssi"] == -52

    def test_ha_ble_temperature_and_humidity(self):
        """Test HA BLE parser for temperature and humidity measurement"""
        data_string = "043E1B02010000A5808FE648540F0201060B161C182302CA090303BF13CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 25.06
        assert sensor_msg["humidity"] == 50.55
        assert sensor_msg["rssi"] == -52

    def test_ha_ble_pressure(self):
        """Test HA BLE parser for pressure measurement"""
        data_string = "043E1B02010000A5808FE648540F0201060B161C1802000C0404138A01DC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == 12
        assert sensor_msg["data"]
        assert sensor_msg["pressure"] == 1008.83
        assert sensor_msg["rssi"] == -36

    def test_ha_ble_illuminance(self):
        """Test HA BLE parser for illuminance measurement"""
        data_string = "043E1802010000A5808FE648540C02010608161C180405138A14DC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["illuminance"] == 13460.67
        assert sensor_msg["rssi"] == -36

    def test_ha_ble_weight(self):
        """Test HA BLE parser for weight measurement"""
        data_string = "043E1B02010000A5808FE648540F0201060B161C1803065E1F63076B67DC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["weight"] == 80.3
        assert sensor_msg["weight unit"] == "kg"
        assert sensor_msg["rssi"] == -36

    def test_ha_ble_dew_point(self):
        """Test HA BLE parser for dew point measurement"""
        data_string = "043E1702010000A5808FE648540B02010607161C182308CA06DC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["dew point"] == 17.38
        assert sensor_msg["rssi"] == -36
