"""The tests for the BTHome (DIY sensor) ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestBTHome:
    """Tests for the BTHome V2 (DIY sensor) parser"""
    def test_bthome_v2_packet_and_battery(self):
        """Test BTHome V2 parser for battery measurement and packet number"""
        data_string = "043E1802010000A5808FE648540C0201060816D2FC4000090161CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == 9
        assert sensor_msg["data"]
        assert sensor_msg["battery"] == 97
        assert sensor_msg["rssi"] == -52

    def test_bhtome_v2_temperature_and_humidity(self):
        """Test BTHome V2 parser for temperature and humidity measurement"""
        data_string = "043E1A02010000A5808FE648540E0201060A16D2FC4002CA0903BF13CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 25.06
        assert sensor_msg["humidity"] == 50.55
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_temperature_and_humidity_encrypted(self):
        """Test BTHome parser for temperature and humidity (encrypted) measurement"""
        self.aeskeys = {}
        data_string = "043E2202010000A5808FE64854160201061216d2fc41a47266c95f730011223378237214CC"
        data = bytes(bytearray.fromhex(data_string))
        aeskey = "231d39c1d7cc1ab1aee224cd096db932"

        p_mac = bytes.fromhex("5448E68F80A5")
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        allow_list = self.aeskeys.keys()

        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys, discovery=False, sensor_whitelist=allow_list)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2 (encrypted)"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == 857870592
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 25.06
        assert sensor_msg["humidity"] == 50.55
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_pressure(self):
        """Test BTHome parser for pressure measurement"""
        data_string = "043E1A02010000A5808FE648540E0201060A16D2FC40000C04138A01DC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == 12
        assert sensor_msg["data"]
        assert sensor_msg["pressure"] == 1008.83
        assert sensor_msg["rssi"] == -36

    def test_bthome_v2_illuminance(self):
        """Test BTHome parser for illuminance measurement"""
        data_string = "043E1802010000A5808FE648540C0201060816D2FC4005138A14DC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["illuminance"] == 13460.67
        assert sensor_msg["rssi"] == -36

    def test_bthome_v2_weight(self):
        """Test BTHome parser for weight measurement"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC40065E1FDC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["weight"] == 80.3
        assert sensor_msg["rssi"] == -36

    def test_bthome_v2_dewpoint(self):
        """Test BTHome parser for dewpoint measurement"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC4008CA06DC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["dewpoint"] == 17.38
        assert sensor_msg["rssi"] == -36

    def test_bthome_v2_energy(self):
        """Test BTHome parser for energy measurement"""
        data_string = "043E1802010000A5808FE648540C0201060816D2FC400A138A14DC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["energy"] == 1346.067
        assert sensor_msg["rssi"] == -36

    def test_bthome_v2_power(self):
        """Test BTHome parser for power measurement"""
        data_string = "043E1802010000A5808FE648540C0201060816D2FC400B021B00DC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["power"] == 69.14
        assert sensor_msg["rssi"] == -36

    def test_bthome_v2_voltage(self):
        """Test BTHome parser for voltage measurement"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC400C020CDC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["voltage"] == 3.074
        assert sensor_msg["rssi"] == -36

    def test_bthome_v2_pm(self):
        """Test BTHome parser for PM2.5 and PM10 measurement"""
        data_string = "043E1A02010000A5808FE648540E0201060A16D2FC400D120C0E021CDC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["pm2.5"] == 3090
        assert sensor_msg["pm10"] == 7170
        assert sensor_msg["rssi"] == -36

    def test_bthome_v2_binary(self):
        """Test BTHome parser for binary sensor measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC400F01CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["binary"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_switch(self):
        """Test BTHome parser for dew point measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC401001DC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["switch"] == 1
        assert sensor_msg["rssi"] == -36

    def test_bthome_v2_opening(self):
        """Test BTHome parser for opening measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC401100CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["opening"] == 0
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_co2(self):
        """Test BTHome parser for co2 measurement"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC4012E204CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["co2"] == 1250
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_tvoc(self):
        """Test BTHome parser for tvoc measurement"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC40133301CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["tvoc"] == 307
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_moisture(self):
        """Test BTHome parser for moisture measurement"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC40143301CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["moisture"] == 3.07
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_door(self):
        """Test BTHome parser for binary door sensor (open/closed)"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC401A01CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["door"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_light(self):
        """Test BTHome parser for binary light sensor (light/dark)"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC401E01CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["light"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_lock(self):
        """Test BTHome parser for binary lock sensor (locked/unlocked)"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC401F01CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["lock"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_motion(self):
        """Test BTHome parser for binary motion sensor (motion detected/no motion)"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC402101CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["motion"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_smoke(self):
        """Test BTHome parser for binary smoke detector (smoke detected/no smoke)"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC402901CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["smoke detector"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_humidity_1_byte(self):
        """Test BTHome parser for humidity measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC402E33CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["humidity"] == 51
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_moisture_1_byte(self):
        """Test BTHome parser for moisture measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC402F33CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["moisture"] == 51
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_count_2_bytes(self):
        """Test BTHome parser for count measurement with 2 bytes"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC403D3321CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["count"] == 8499
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_count_4_bytes(self):
        """Test BTHome parser for count measurement with 4 bytes"""
        data_string = "043E1902010000A5808FE648540D0201060916D2FC403E33AE3221CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["count"] == 556969523
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_temperature_2_bytes_1_digit(self):
        """Test BTHome parser for temperature measurement with 2 bytes and 1 digit"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC40450101CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 25.7
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_double_temperature(self):
        """Test BTHome parser for double temperature measurement, which isn't supported (yet)"""
        data_string = "043E1A02010000A5808FE648540E0201060A16D2FC40450101450301CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 25.9
        assert sensor_msg["rssi"] == -52
