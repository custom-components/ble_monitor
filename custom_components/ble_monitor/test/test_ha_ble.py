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

    def test_ha_ble_pressure(self):
        """Test HA BLE parser for pressure measurement"""
        data_string = "043E1F02010000A5808FE6485413020106070848415F424C4507166D2A78091000CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["pressure"] == 1051.0
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

    def test_ha_ble_temperature_packet_nr(self):
        """Test HA BLE parser for temperature measurement with packet number """
        data_string = "043E2202010000A5808FE6485416020106070848415F424C4504164D2A0605166E2A3409CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == 6
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 23.56
        assert sensor_msg["rssi"] == -52

    def test_ha_ble_humidity(self):
        """Test HA BLE parser for humidity measurement"""
        data_string = "043E1D02010000A5808FE6485411020106070848415F424C4505166F2A5419CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["humidity"] == 64.84
        assert sensor_msg["rssi"] == -52

    def test_ha_ble_dewpoint(self):
        """Test HA BLE parser for dewpoint measurement"""
        data_string = "043e1c02010000a5808fe6485410020106070848415f424c4504167b2a18cc"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["dewpoint"] == 24
        assert sensor_msg["rssi"] == -52

    def test_ha_ble_weight_kg(self):
        """Test HA BLE parser for weight measurement in kg"""
        data_string = "043E1E02010000A5808FE6485412020106070848415F424C450616982A00AA33CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["weight"] == 66.13
        assert sensor_msg["weight unit"] == "kg"
        assert sensor_msg["rssi"] == -52

    def test_ha_ble_weight_lbs(self):
        """Test HA BLE parser for weight measurement in lbs"""
        data_string = "043E1E02010000A5808FE6485412020106070848415F424C450616982A01AA33CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["weight"] == 132.26
        assert sensor_msg["weight unit"] == "lbs"
        assert sensor_msg["rssi"] == -52

    def test_ha_ble_binary(self):
        """Test HA BLE parser for binary measurement"""
        data_string = "043e1c02010000a5808fe6485410020106070848415f424c450416e22a01cc"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["binary"] == 1
        assert sensor_msg["rssi"] == -52

    def test_ha_ble_count16(self):
        """Test HA BLE parser for count16 measurement"""
        data_string = "043E1D02010000A5808FE6485411020106070848415F424C450516EA2A22FFCC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["count"] == 65314
        assert sensor_msg["rssi"] == -52

    def test_ha_ble_count24(self):
        """Test HA BLE parser for count24 measurement"""
        data_string = "043E1E02010000A5808FE6485412020106070848415F424C450616EB2AFFFFFFCC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["count"] == "unknown"
        assert sensor_msg["rssi"] == -52

    def test_ha_ble_energy(self):
        """Test HA BLE parser for energy measurement"""
        data_string = "043E1F02010000A5808FE6485413020106070848415F424C450716F22A81121000CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["energy"] == 1053.313
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

    def test_ha_ble_power(self):
        """Test HA BLE parser for power measurement"""
        data_string = "043E1E02010000A5808FE6485412020106070848415F424C450616052B510A00CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["power"] == 264.1
        assert sensor_msg["rssi"] == -52

    def test_ha_ble_voltage(self):
        """Test HA BLE parser for voltage measurement"""
        data_string = "043E1D02010000A5808FE6485411020106070848415F424C450516182BB400CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["voltage"] == 2.8125
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

    def test_ha_ble_voltage_power(self):
        """Test HA BLE parser for voltage + power measurement"""
        data_string = "043E2402010000A5808FE6485418020106070848415F424C450516182BB4000616052B510A00CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "HA BLE"
        assert sensor_msg["type"] == "HA BLE DIY"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["voltage"] == 2.8125
        assert sensor_msg["power"] == 264.1
        assert sensor_msg["rssi"] == -52
