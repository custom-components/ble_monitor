"""The tests for the ATC ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestATC:
    """Tests for the ATC parser"""

    def test_atc_atc1441(self):
        """Test ATC parser for ATC 1441 format."""
        data_string = "043e1d02010000f4830238c1a41110161a18a4c1380283f400a22f5f0bf819df"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "ATC (Atc1441)"
        assert sensor_msg["type"] == "ATC"
        assert sensor_msg["mac"] == "A4C1380283F4"
        assert sensor_msg["packet"] == 25
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 16.2
        assert sensor_msg["humidity"] == 47
        assert sensor_msg["voltage"] == 3.064
        assert sensor_msg["battery"] == 95
        assert sensor_msg["rssi"] == -33

    def test_atc_atc1441_ext(self):
        """Test ATC parser for ATC 1441 format (extended advertisement)."""
        data_string = "043E2B0D011300004E7CBC38C1A40100FF7FB90000000000000000001110161A18A4C138BC7C4E0102284F0B6720"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "ATC (Atc1441)"
        assert sensor_msg["type"] == "ATC"
        assert sensor_msg["mac"] == "A4C138BC7C4E"
        assert sensor_msg["packet"] == 32
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 25.8
        assert sensor_msg["humidity"] == 40
        assert sensor_msg["voltage"] == 2.919
        assert sensor_msg["battery"] == 79
        assert sensor_msg["rssi"] == -71

    def test_atc_custom(self):
        """Test ATC parser for ATC custom format."""
        data_string = "043e1f02010000f4830238c1a41312161a18f4830238c1a4a9066911b60b58f70dde"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "ATC (Custom)"
        assert sensor_msg["type"] == "ATC"
        assert sensor_msg["mac"] == "A4C1380283F4"
        assert sensor_msg["packet"] == 247
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 17.05
        assert sensor_msg["humidity"] == 44.57
        assert sensor_msg["voltage"] == 2.998
        assert sensor_msg["battery"] == 88
        assert sensor_msg["rssi"] == -34

    def test_atc_custom_v2_9(self):
        """Test ATC parser for ATC custom format (firmware version 2.9 and above)."""
        data_string = "043E2202010000B2188D38C1A41602010612161A18B2188D38C1A42B089011F70A43200FC2"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "ATC (Custom)"
        assert sensor_msg["type"] == "ATC"
        assert sensor_msg["mac"] == "A4C1388D18B2"
        assert sensor_msg["packet"] == 32
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 20.91
        assert sensor_msg["humidity"] == 44.96
        assert sensor_msg["voltage"] == 2.807
        assert sensor_msg["battery"] == 67
        assert sensor_msg["rssi"] == -62

    def test_atc_custom_ext(self):
        """Test ATC parser for ATC custom format (extended format)."""
        data_string = "043E300D011300008B376338C1A40100FF7FBA0000000000000000001602010612161A188B376338C1A4CE0913107F0B521204"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "ATC (Custom)"
        assert sensor_msg["type"] == "ATC"
        assert sensor_msg["mac"] == "A4C13863378B"
        assert sensor_msg["packet"] == 18
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 25.1
        assert sensor_msg["humidity"] == 41.15
        assert sensor_msg["voltage"] == 2.943
        assert sensor_msg["battery"] == 82
        assert sensor_msg["rssi"] == -70

    def test_atc_custom_encrypted(self):
        """Test ATC parser for ATC custom format (encrypted)."""
        self.aeskeys = {}
        data_string = "043e1b02010000b2188d38c1a40f0e161a1811d603fbfa7b6dfb1e26fde2"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "b9ea895fac7eea6d30532432a516f3a3"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "ATC (Custom encrypted)"
        assert sensor_msg["type"] == "ATC"
        assert sensor_msg["mac"] == "A4C1388D18B2"
        assert sensor_msg["packet"] == 17
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 23.45
        assert sensor_msg["humidity"] == 41.73
        assert sensor_msg["voltage"] == 2.749
        assert sensor_msg["battery"] == 61
        assert sensor_msg["rssi"] == -30
