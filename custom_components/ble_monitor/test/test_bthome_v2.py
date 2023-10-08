"""The tests for the BTHome (DIY sensor) ble_parser."""
import datetime

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

    def test_bthome_v2_battery_low(self):
        """Test BTHome parser for battery low measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC401501CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["battery low"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_battery_charging(self):
        """Test BTHome parser for battery charging measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC401601CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["battery charging"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_carbon_monoxide(self):
        """Test BTHome parser for carbon monoxide measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC401701CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["carbon monoxide"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_cold(self):
        """Test BTHome parser for cold measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC401801CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["cold"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_connectivity(self):
        """Test BTHome parser for connectivity measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC401901CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["connectivity"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_door(self):
        """Test BTHome parser for door measurement"""
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

    def test_bthome_v2_garage_door(self):
        """Test BTHome parser for garage door measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC401B01CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["garage door"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_gas_detected(self):
        """Test BTHome parser for gas detected measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC401C00CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["gas detected"] == 0
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_heat(self):
        """Test BTHome parser for heat measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC401D01CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["heat"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_light(self):
        """Test BTHome parser for light measurement"""
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
        """Test BTHome parser for lock measurement"""
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

    def test_bthome_v2_moisture_detected(self):
        """Test BTHome parser for moisture detected measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC402001CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["moisture detected"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_motion(self):
        """Test BTHome parser for motion measurement"""
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

    def test_bthome_v2_moving(self):
        """Test BTHome parser for moving measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC402201CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["moving"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_occupancy(self):
        """Test BTHome parser for occupancy measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC402300CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["occupancy"] == 0
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_plug(self):
        """Test BTHome parser for plug measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC402401CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["plug"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_presence(self):
        """Test BTHome parser for presence measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC402501CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["presence"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_problem(self):
        """Test BTHome parser for problem measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC402601CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["problem"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_running(self):
        """Test BTHome parser for running measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC402700CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["running"] == 0
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_safety(self):
        """Test BTHome parser for safety measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC402801CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["safety"] == 1
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
        assert sensor_msg["smoke"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_sound(self):
        """Test BTHome parser for binary sound detector"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC402A01CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["sound"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_tamper(self):
        """Test BTHome parser for binary tamper detector"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC402B01CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["tamper"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_vibration(self):
        """Test BTHome parser for binary vibration sensor"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC402C01CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["vibration"] == 1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_window(self):
        """Test BTHome parser for binary window sensor"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC402D01CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["window"] == 1
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

    def test_bthome_v2_button(self):
        """Test BTHome parser for button sensor measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC403A02CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["button"] == "double press"
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_dimmer(self):
        """Test BTHome parser for dimmer sensor measurement"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC403C0103CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["dimmer"] == "rotate left"
        assert sensor_msg["steps"] == 3
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

    def test_bthome_v2_rotation(self):
        """Test BTHome parser for rotation measurement"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC403F020CCC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["rotation"] == 307.4
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_distance_mm(self):
        """Test BTHome parser for distance measurement"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC40400C00CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["distance mm"] == 12
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_distance_m(self):
        """Test BTHome parser for distance measurement"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC40414E00CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["distance"] == 7.8
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_duration(self):
        """Test BTHome parser for distance measurement"""
        data_string = "043E1802010000A5808FE648540C0201060816D2FC40424E3400CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["duration"] == 13.390
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_current(self):
        """Test BTHome parser for current measurement"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC40434E34CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["current"] == 13.39
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_speed(self):
        """Test BTHome parser for speed measurement"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC40444E34CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["speed"] == 133.90
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_temperature_1_digit(self):
        """Test BTHome parser for temperature measurement"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC40451101CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 27.3
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_uv_index(self):
        """Test BTHome parser for uv_index measurement"""
        data_string = "043E1602010000A5808FE648540A0201060616D2FC404632CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["uv index"] == 5.0
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_volume_liter(self):
        """Test BTHome parser for volume measurement in liter"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC40478756CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["volume"] == 2215.1
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_volume_milliliter(self):
        """Test BTHome parser for volume measurement in milliliter"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC4048DC87CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["volume mL"] == 34780
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_volume_flow_rate(self):
        """Test BTHome parser for volume flow rate measurement"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC4049DC87CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["volume flow rate"] == 34.78
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_voltage_1_digit(self):
        """Test BTHome parser for voltage measurement with 1 digit"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC404A020CCC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["voltage"] == 307.4
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_gas_3_bytes(self):
        """Test BTHome parser for gas measurement with 3 bytes"""
        data_string = "043E1802010000A5808FE648540C0201060816D2FC404B138A14CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["gas"] == 1346.067
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_gas_4_bytes(self):
        """Test BTHome parser for gas measurement with 4 bytes"""
        data_string = "043E1902010000A5808FE648540D0201060916D2FC404C41018A01CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["gas"] == 25821.505
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_energy_4_bytes(self):
        """Test BTHome parser for energy measurement with 4 bytes"""
        data_string = "043E1902010000A5808FE648540D0201060916D2FC404D12138A14CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["energy"] == 344593.170
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_volume_4_bytes(self):
        """Test BTHome parser for volume measurement with 4 bytes"""
        data_string = "043E1902010000A5808FE648540D0201060916D2FC404E87562A01CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["volume"] == 19551.879
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_water_4_bytes(self):
        """Test BTHome parser for water measurement with 4 bytes"""
        data_string = "043E1902010000A5808FE648540D0201060916D2FC404F87562A01CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["water"] == 19551.879
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_timestamp(self):
        """Test BTHome parser for timestamp measurement"""
        data_string = "043E1902010000A5808FE648540D0201060916D2FC40505d396164CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["timestamp"] == datetime.datetime(2023, 5, 14, 19, 41, 17, tzinfo=datetime.timezone.utc)
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_acceleration(self):
        """Test BTHome parser for acceleration measurement"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC40518756CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["acceleration"] == 22.151
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_gyroscope(self):
        """Test BTHome parser for gyroscope measurement"""
        data_string = "043E1702010000A5808FE648540B0201060716D2FC40528756CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["gyroscope"] == 22.151
        assert sensor_msg["rssi"] == -52

    def test_bthome_v2_text(self):
        """Test BTHome parser for text measurement"""
        data_string = "043E2202010000A5808FE64854160201061216D2FC40530C48656C6C6F20576F726C6421CC"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "BTHome V2"
        assert sensor_msg["type"] == "BTHome"
        assert sensor_msg["mac"] == "5448E68F80A5"
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["text"] == "Hello World!"
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
