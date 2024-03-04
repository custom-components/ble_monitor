"""The tests for the Xiaomi ble_parser."""
import datetime

from ble_monitor.ble_parser import BleParser


class TestXiaomi:
    """Tests for the Xiaomi parser"""

    def test_Xiaomi_LYWSDCGQ(self):
        """Test Xiaomi parser for LYWSDCGQ."""
        data_string = "043e2502010000219335342d5819020106151695fe5020aa01da219335342d580d1004fe004802c4"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V2)"
        assert sensor_msg["type"] == "LYWSDCGQ"
        assert sensor_msg["mac"] == "582D34359321"
        assert sensor_msg["packet"] == 218
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 25.4
        assert sensor_msg["humidity"] == 58.4
        assert sensor_msg["rssi"] == -60

    def test_Xiaomi_CGG1(self):
        """Test Xiaomi parser for CGG1."""
        self.aeskeys = {}
        data_string = "043e2a020100005f12342d585a1e0201061a1695fe5858480b685f12342d585a0b1841e2aa000e00a4964fb5b6"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "814aac74c4f17b6c1581e1ab87816b99"

        p_mac = bytes.fromhex("5A582D34125F")
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        allow_list = self.aeskeys.keys()

        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys, discovery=False, sensor_whitelist=allow_list)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "CGG1-ENCRYPTED"
        assert sensor_msg["mac"] == "5A582D34125F"
        assert sensor_msg["packet"] == 104
        assert sensor_msg["data"]
        assert sensor_msg["humidity"] == 59.6
        assert sensor_msg["rssi"] == -74

    def test_Xiaomi_CGDK2(self):
        """Test Xiaomi parser for CGDK2."""
        self.aeskeys = {}
        data_string = "043e2a02010000892012342d581e0201061a1695fe58586f0607892012342d585f176dd54f0200002fa453faaf"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "a3bfe9853dd85a620debe3620caaa351"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "CGDK2"
        assert sensor_msg["mac"] == "582D34122089"
        assert sensor_msg["packet"] == 7
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 22.6
        assert sensor_msg["rssi"] == -81

    def test_Xiaomi_LYWSD02(self):
        """Test Xiaomi parser for LYWSD02."""

    def test_Xiaomi_LYWSD03MMC(self):
        """Test Xiaomi parser for LYWSD03MMC without encryption."""
        data_string = "043e22020100004c94b438c1a416151695fe50305b05034c94b438c1a40d10041001ea01cf"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V3)"
        assert sensor_msg["type"] == "LYWSD03MMC"
        assert sensor_msg["mac"] == "A4C138B4944C"
        assert sensor_msg["packet"] == 3
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 27.2
        assert sensor_msg["humidity"] == 49.0
        assert sensor_msg["rssi"] == -49

    def test_Xiaomi_LYWSD02MMC(self):
        """Test Xiaomi parser for LYWSD02MMC."""
        self.aeskeys = {}
        data_string = "043e290201000084535638c1a41d020106191695fe5858e4162c84535638c1a42b6ef2e91200006c884d9eb0"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "a115210eed7a88e50ad52662e732a9fb"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "LYWSD02MMC"
        assert sensor_msg["mac"] == "A4C138565384"
        assert sensor_msg["packet"] == 44
        assert sensor_msg["data"]
        assert sensor_msg["humidity"] == 58
        assert sensor_msg["rssi"] == -80

    def test_Xiaomi_LYWSD03MMC_encrypted(self):
        """Test Xiaomi parser for LYWSD03MMC with encryption."""
        self.aeskeys = {}
        data_string = "043e2a02010000f4830238c1a41e0201061a1695fe58585b0550f4830238c1a495ef58763c26000097e2abb5e2"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "e9ea895fac7cca6d30532432a516f3a8"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "LYWSD03MMC"
        assert sensor_msg["mac"] == "A4C1380283F4"
        assert sensor_msg["packet"] == 80
        assert sensor_msg["data"]
        assert sensor_msg["humidity"] == 46.7
        assert sensor_msg["rssi"] == -30

    def test_Xiaomi_XMWSDJ04MMC(self):
        """Test Xiaomi parser for XMWSDJ04MMC with encryption."""
        self.aeskeys = {}
        data_string = "043e260201000004702565112c1a020106161695fe48590312a41b776e7c96add7000000f2bf545bce"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "b2cf9a553d53571b5657defd582d676e"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "XMWSDJ04MMC"
        assert sensor_msg["mac"] == "2C1165257004"
        assert sensor_msg["packet"] == 164
        assert sensor_msg["data"]
        assert sensor_msg["humidity"] == 45.0
        assert sensor_msg["rssi"] == -50

    def test_Xiaomi_XMMF01JQD(self):
        """Test Xiaomi parser for XMMF01JQD."""
        data_string = "043e240201000154d3e63053e218020106141695fe5030e1048e54d3e63053e2011003010000b8"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V3)"
        assert sensor_msg["type"] == "XMMF01JQD"
        assert sensor_msg["mac"] == "E25330E6D354"
        assert sensor_msg["packet"] == 142
        assert sensor_msg["data"]
        assert sensor_msg["button"] == "left"
        assert sensor_msg["rssi"] == -72

    def test_Xiaomi_CGC1(self):
        """Test Xiaomi parser for CGC1."""

    def test_Xiaomi_CGD1(self):
        """Test Xiaomi parser for CGD1."""

    def test_Xiaomi_CGP1W(self):
        """Test Xiaomi parser for CGP1W."""

    def test_Xiaomi_MHO_C303(self):
        """Test Xiaomi parser for MHO-C303."""

    def test_Xiaomi_MHO_C401(self):
        """Test Xiaomi parser for MHO-C401."""

    def test_Xiaomi_JQJCY01YM1(self):
        """Test Xiaomi parser for JQJCY01YM."""

    def test_Xiaomi_JTYJGD03MI_smoke(self):
        """Test Xiaomi parser for JTYJGD03MI."""
        self.aeskeys = {}
        data_string = "043e2902010000bc9ce344ef541d020106191695fe5859970966bc9ce344ef5401081205000000715ebe90cb"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "5b51a7c91cde6707c9ef18dfda143a58"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "JTYJGD03MI"
        assert sensor_msg["mac"] == "54EF44E39CBC"
        assert sensor_msg["packet"] == 102
        assert sensor_msg["data"]
        assert sensor_msg["smoke"] == 1
        assert sensor_msg["rssi"] == -53

    def test_Xiaomi_JTYJGD03MI_press(self):
        """Test Xiaomi parser for JTYJGD03MI."""
        self.aeskeys = {}
        data_string = "043e2b02010000bc9ce344ef541f0201061b1695fe5859970964bc9ce344ef5422206088fd000000003a148fb3cb"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "5b51a7c91cde6707c9ef18dfda143a58"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "JTYJGD03MI"
        assert sensor_msg["mac"] == "54EF44E39CBC"
        assert sensor_msg["packet"] == 100
        assert sensor_msg["data"]
        assert sensor_msg["button"] == "single press"
        assert sensor_msg["rssi"] == -53

    def test_Xiaomi_HHCCJCY01(self):
        """Test Xiaomi parser for HHCCJCY01."""
        data_string = "043e2802010000f34f6b8d7cc41c020106030295fe141695fe7120980012f34f6b8d7cc40d041002c400a9"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V2)"
        assert sensor_msg["type"] == "HHCCJCY01"
        assert sensor_msg["mac"] == "C47C8D6B4FF3"
        assert sensor_msg["packet"] == 18
        assert sensor_msg["temperature"] == 19.6
        assert sensor_msg["data"]
        assert sensor_msg["rssi"] == -87

    def test_Xiaomi_GCLS002(self):
        """Test Xiaomi parser for GCLS002 / HHCCJCY09."""
        data_string = "043E28020100003E596D8D7CC41C020106030295FE141695FE7120BC03CD3E596D8D7CC40D0410023C01A8"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V2)"
        assert sensor_msg["type"] == "GCLS002"
        assert sensor_msg["mac"] == "C47C8D6D593E"
        assert sensor_msg["packet"] == 205
        assert sensor_msg["temperature"] == 31.6
        assert sensor_msg["data"]
        assert sensor_msg["rssi"] == -88

    def test_Xiaomi_HHCCPOT002(self):
        """Test Xiaomi parser for HHCCPOT002."""

    def test_Xiaomi_WX08ZM(self):
        """Test Xiaomi parser for WX08ZM."""

    def test_Xiaomi_MCCGQ02HL(self):
        """Test Xiaomi parser for MCCGQ02HL."""

    def test_Xiaomi_CGH1(self):
        """Test Xiaomi parser for CGH1."""

    def test_Xiaomi_YM_K1501(self):
        """Test Xiaomi parser for YM-K1501."""

    def test_Xiaomi_V_SK152(self):
        """Test Xiaomi parser for V-SK152."""

    def test_Xiaomi_SJWS01LM(self):
        """Test Xiaomi parser for SJWS01LM."""
        self.aeskeys = {}
        data_string = "043e2902010000bc27e044ef541d020106191695fe5859630808bc27e044ef54f58fe704000000fc69d15ca8"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "255e6cabb39b2eddd0de992b9fee2bf2"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "SJWS01LM"
        assert sensor_msg["mac"] == "54EF44E027BC"
        assert sensor_msg["packet"] == 8
        assert sensor_msg["data"]
        assert sensor_msg["moisture detected"]
        assert sensor_msg["rssi"] == -88

    def test_Xiaomi_RS1BB(self):
        """Test Xiaomi parser for LINP-RS1BB."""
        self.aeskeys = {}
        data_string = "043E2902010000674cb938c1a41d020106191695fe58590F3F4A674CB938C1A4D6E57B83040000D01E0B4BC0"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "33ede53321bc73c790a8daae4581f3d5"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "RS1BB"
        assert sensor_msg["mac"] == "A4C138B94C67"
        assert sensor_msg["packet"] == 74
        assert sensor_msg["data"]
        assert sensor_msg["moisture detected"] == 0
        assert sensor_msg["rssi"] == -64

    def test_Xiaomi_MJYD02YL(self):
        """Test Xiaomi parser for MJYD02YL."""

    def test_Xiaomi_MUE4094RT(self):
        """Test Xiaomi parser for MUE4094RT."""
        data_string = "043e1c020102010c39b2e870de100201060c1695fe4030dd032403000101c6"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V3)"
        assert sensor_msg["type"] == "MUE4094RT"
        assert sensor_msg["mac"] == "DE70E8B2390C"
        assert sensor_msg["packet"] == 36
        assert sensor_msg["data"]
        assert sensor_msg["motion"] == 1
        assert sensor_msg["motion timer"] == 1
        assert sensor_msg["rssi"] == -58

    def test_Xiaomi_RTCGQ02LM(self):
        """Test Xiaomi parser for RTCGQ02LM with wrong encryption key."""
        self.aeskeys = {}
        data_string = "043e2b020103000fc4e044ef541f0201061b1695fe58598d0a170fc4e044ef547cc27a5c03a1000000790df258bb"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "FFD8CE9C08AE7533A79BDAF0BB755E96"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "RTCGQ02LM"
        assert sensor_msg["mac"] == "54EF44E0C40F"
        assert sensor_msg["packet"] == 23
        assert sensor_msg["data"] is False
        assert sensor_msg["rssi"] == -69

    def test_Xiaomi_CGPR1(self):
        """Test Xiaomi parser for CGPR1."""

    def test_Xiaomi_MMC_T201_1(self):
        """Test Xiaomi parser for MMC-T201-1."""
        data_string = "043e2b02010000c16fddf981001f02010603020918171695fe7022db006fc16fddf9810009002005c60d630d51b1"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V2)"
        assert sensor_msg["type"] == "MMC-T201-1"
        assert sensor_msg["mac"] == "0081F9DD6FC1"
        assert sensor_msg["packet"] == 111
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 36.87199806168224
        assert sensor_msg["battery"] == 81
        assert sensor_msg["rssi"] == -79

    def test_Xiaomi_MMC_W505(self):
        """Test Xiaomi parser for MMC-W505."""
        data_string = "043e4a02010201dbab531824d03e02010603020918151695fe702291030fdbab531824d0090a0002750d0709094d4d432d573530350000000000000000000000000000000000000000000000c6"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V2)"
        assert sensor_msg["type"] == "MMC-W505"
        assert sensor_msg["mac"] == "D0241853ABDB"
        assert sensor_msg["packet"] == 15
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 34.45
        assert sensor_msg["rssi"] == -58

    def test_Xiaomi_M1S_T500(self):
        """Test Xiaomi parser for M1S-T500."""
        data_string = "043e2402010001115b174371e618020106141695fe7130890437115b174371e6091000020003dc"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V3)"
        assert sensor_msg["type"] == "M1S-T500"
        assert sensor_msg["mac"] == "E67143175B11"
        assert sensor_msg["packet"] == 55
        assert sensor_msg["data"]
        assert sensor_msg["toothbrush"] == 1
        assert sensor_msg["counter"] == 3
        assert sensor_msg["rssi"] == -36

    def test_Xiaomi_T700(self):
        """Test Xiaomi parser for T700."""
        self.aeskeys = {}
        data_string = "043e28020102010c483f34deed1c020106181695fe48580608c9480ef11281079733fc1400005644db41c6"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "1330b99cded13258acc391627e9771f7"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "T700"
        assert sensor_msg["mac"] == "EDDE343F480C"
        assert sensor_msg["packet"] == 201
        assert sensor_msg["data"]
        assert sensor_msg["toothbrush"] == 0
        assert sensor_msg["score"] == 83
        assert sensor_msg["end time"] == datetime.datetime(2023, 6, 29, 10, 50, 43)
        assert sensor_msg["rssi"] == -58

    def test_Xiaomi_ZNMS16LM_fingerprint(self):
        """Test Xiaomi parser for ZNMS16LM."""
        data_string = "043e2a02010000918aeb441fd71e020106030295fe161695fe50449e0642918aeb441fd7060005ffffffff00a9"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V4)"
        assert sensor_msg["type"] == "ZNMS16LM"
        assert sensor_msg["mac"] == "D71F44EB8A91"
        assert sensor_msg["packet"] == 66
        assert sensor_msg["data"]
        assert sensor_msg["fingerprint"] == 1
        assert sensor_msg["result"] == "match successful"
        assert sensor_msg["key id"] == "unknown operator"
        assert sensor_msg["rssi"] == -87

    def test_Xiaomi_ZNMS16LM_lock(self):
        """Test Xiaomi parser for ZNMS16LM."""
        data_string = "043e2e02010000918aeb441fd722020106030295fe1a1695fe50449e0643918aeb441fd70b000920020001807c442f61a9"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V4)"
        assert sensor_msg["type"] == "ZNMS16LM"
        assert sensor_msg["mac"] == "D71F44EB8A91"
        assert sensor_msg["packet"] == 67
        assert sensor_msg["data"]
        assert sensor_msg["lock"] == 1
        assert sensor_msg["action"] == "unlock outside the door"
        assert sensor_msg["method"] == "biometrics"
        assert sensor_msg["error"] is None
        assert sensor_msg["key id"] == 2
        assert sensor_msg["rssi"] == -87

    def test_Xiaomi_SV40_door(self):
        """Test Xiaomi parser for Lockin SV40."""
        self.aeskeys = {}
        data_string = "043E27020100003d04a3330c981B020106171695fe4855c211144e28703276fccd3d00000080e72280C0"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "54d84797cb77f9538b224b305c877d1e"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "SV40"
        assert sensor_msg["mac"] == "980C33A3043D"
        assert sensor_msg["packet"] == 20
        assert sensor_msg["data"]
        assert sensor_msg["door"] == 0
        assert sensor_msg["door action"] == "close the door"
        assert sensor_msg["rssi"] == -64

    def test_Xiaomi_SV40_lock(self):
        """Test Xiaomi parser for Lockin SV40."""
        self.aeskeys = {}
        data_string = "043E2B020100003d04a3330c981F0201061b1695fe4855c211165068b6fe3c878095c8a5834f000000463221c6C0"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "54d84797cb77f9538b224b305c877d1e"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "SV40"
        assert sensor_msg["mac"] == "980C33A3043D"
        assert sensor_msg["packet"] == 22
        assert sensor_msg["data"]
        assert sensor_msg["lock"] == 1
        assert sensor_msg["locktype"] == "lock"
        assert sensor_msg["action"] == "unlock inside the door"
        assert sensor_msg["method"] == "automatic"
        assert sensor_msg["error"] is None
        assert sensor_msg["key id"] == 0
        assert sensor_msg["rssi"] == -64

    def test_Xiaomi_YLAI003(self):
        """Test Xiaomi parser for YLAI003."""

    def test_Xiaomi_YLYK01YL(self):
        """Test Xiaomi parser for YLYK01YL."""
        data_string = "043E21020103007450E94124F815141695FE503053013F7450E94124F8011003000000E0"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V3)"
        assert sensor_msg["type"] == "YLYK01YL"
        assert sensor_msg["mac"] == "F82441E95074"
        assert sensor_msg["packet"] == 63
        assert sensor_msg["data"]
        assert sensor_msg["remote"] == "on"
        assert sensor_msg["button"] == "single press"
        assert sensor_msg["remote single press"] == 1
        assert sensor_msg["rssi"] == -32

    def test_Xiaomi_YLYK01YL_FANCL(self):
        """Test Xiaomi parser for YLYK01YL-FANCL."""

    def test_Xiaomi_YLYK01YL_VENFAN(self):
        """Test Xiaomi parser for YLYK01YL-VENFAN."""

    def test_Xiaomi_YLYB01YL_BHFRC(self):
        """Test Xiaomi parser for YLYB01YL-BHFRC."""

    def test_Xiaomi_YLKG07YL_press(self):
        """Test Xiaomi parser for YLKG07YL, YLKG08YL while pressing dimmer (no rotation)."""
        self.aeskeys = {}
        data_string = "043E25020103008B98C54124F819181695FE5830B603D28B98C54124F8C3491476757E00000099DE"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "b853075158487ca39a5b5ea9"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V3 encrypted)"
        assert sensor_msg["type"] == "YLKG07YL/YLKG08YL"
        assert sensor_msg["mac"] == "F82441C5988B"
        assert sensor_msg["packet"] == 210
        assert sensor_msg["data"]
        assert sensor_msg["steps"] == 1
        assert sensor_msg["dimmer"] == "short press"
        assert sensor_msg["rssi"] == -34

    def test_Xiaomi_YLKG07YL_rotate(self):
        """Test Xiaomi parser for YLKG07YL, YLKG08YL while rotating dimmer."""
        self.aeskeys = {}
        data_string = "043e25020103008b98c54124f819181695fe5830b603368b98c54124f88bb8f2661351000000d6ef"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "b853075158487ca39a5b5ea9"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V3 encrypted)"
        assert sensor_msg["type"] == "YLKG07YL/YLKG08YL"
        assert sensor_msg["mac"] == "F82441C5988B"
        assert sensor_msg["packet"] == 54
        assert sensor_msg["data"]
        assert sensor_msg["steps"] == 1
        assert sensor_msg["dimmer"] == "rotate left"
        assert sensor_msg["rssi"] == -17

    def test_Xiaomi_K9B(self):
        """Test Xiaomi parser for K9B."""

    def test_Xiaomi_XMWXKG01YL(self):
        """Test Xiaomi parser for XMWXKG01YL."""

    def test_Xiaomi_DSL_C08(self):
        """Test Xiaomi parser for DSL-C08."""

    def test_Linptech_M1SBB_4A12(self):
        """Test Xiaomi parser for Linptech MS1BB(MI) with 0x4a12 data packet."""
        self.aeskeys = {}
        data_string = "043E290201030067e56638c1a41d020106191695fe585989189a67e56638c1a49dd97af3260000c8a60bd5DE"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "0fdcc30fe9289254876b5ef7c11ef1f0"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "MS1BB(MI)"
        assert sensor_msg["mac"] == "A4C13866E567"
        assert sensor_msg["packet"] == 154
        assert sensor_msg["data"]
        assert sensor_msg["opening"] == 1
        assert sensor_msg["rssi"] == -34

    def test_Linptech_M1SBB(self):
        """Test Xiaomi parser for Linptech MS1BB(MI) with 0x4804 data packet."""
        self.aeskeys = {}
        data_string = "043E290201030067e56638c1a41d020106191695fe585989187667e56638c1a4aa8902ba26000023c3bca8DE"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "0fdcc30fe9289254876b5ef7c11ef1f0"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "MS1BB(MI)"
        assert sensor_msg["mac"] == "A4C13866E567"
        assert sensor_msg["packet"] == 118
        assert sensor_msg["data"]
        assert sensor_msg["opening"] == 1
        assert sensor_msg["rssi"] == -34

    def test_Xiaomi_XMZNMS08LM_lock(self):
        """Test Xiaomi parser for XMZNMS08LM lock."""
        self.aeskeys = {}
        data_string = "043E2B0201000198BE447389EE1F0201061B1695FE4855390E35BF9FD9A08BEFF236EC5BD8315300008E550B6EBE"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "2c3795afa33019a8afdc17ba99e6f217"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "XMZNMS08LM"
        assert sensor_msg["mac"] == "EE897344BE98"
        assert sensor_msg["packet"] == 53
        assert sensor_msg["data"]
        assert sensor_msg["lock"] == 1
        assert sensor_msg["locktype"] == "lock"
        assert sensor_msg["action"] == "unlock outside the door"
        assert sensor_msg["method"] == "biometrics"
        assert sensor_msg["error"] is None
        assert sensor_msg["key id"] == 2
        assert sensor_msg["rssi"] == -66

    def test_Xiaomi_XMZNMS08LM_door(self):
        """Test Xiaomi parser for XMZNMS08LM door."""
        self.aeskeys = {}
        data_string = "043E270201000198BE447389EE1B020106171695FE4855390E339C71C0241FFFEE8053000002B4C539C0"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "2c3795afa33019a8afdc17ba99e6f217"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "XMZNMS08LM"
        assert sensor_msg["mac"] == "EE897344BE98"
        assert sensor_msg["packet"] == 51
        assert sensor_msg["data"]
        assert sensor_msg["door"] == 0
        assert sensor_msg["door action"] == "close the door"
        assert sensor_msg["rssi"] == -64

    def test_linptech_HS1BB_battery(self):
        """Test Xiaomi parser for linptech HS1BB battery."""
        self.aeskeys = {}
        data_string = "043E2902010001e98e0538c1a41D020106191695fe5859eb2a9ee98e0538c1a4d07ad3e338000033635d10C6"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "7475a4a77584401780ffc3ee62dd353c"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "HS1BB(MI)"
        assert sensor_msg["mac"] == "A4C138058EE9"
        assert sensor_msg["packet"] == 158
        assert sensor_msg["data"]
        assert sensor_msg["battery"] == 100
        assert sensor_msg["rssi"] == -58

    def test_linptech_HS1BB_no_motion(self):
        """Test Xiaomi parser for linptech HS1BB no motion (not used in HA)."""
        self.aeskeys = {}
        data_string = "043E2A02010001e98e0538c1a41E0201061a1695fe5859eb2ac1e98e0538c1a40759530f8d380000b77a70f8C6"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "7475a4a77584401780ffc3ee62dd353c"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "HS1BB(MI)"
        assert sensor_msg["mac"] == "A4C138058EE9"
        assert sensor_msg["packet"] == 193
        assert sensor_msg["data"]
        assert sensor_msg["motion"] == 0
        assert sensor_msg["no motion time"] == 60
        assert sensor_msg["rssi"] == -58

    def test_linptech_HS1BB_illuminance_motion(self):
        """Test Xiaomi parser for linptech HS1BB illuminance and motion."""
        self.aeskeys = {}
        data_string = "043E2602010001e98e0538c1a41A020106161695fe4859eb2ac2fce02ca0b43af2380000a2d9f05fC6"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "7475a4a77584401780ffc3ee62dd353c"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "HS1BB(MI)"
        assert sensor_msg["mac"] == "A4C138058EE9"
        assert sensor_msg["packet"] == 194
        assert sensor_msg["data"]
        assert sensor_msg["motion"] == 1
        assert sensor_msg["motion timer"] == 1
        assert sensor_msg["illuminance"] == 228.0
        assert sensor_msg["rssi"] == -58

    def test_MJZNZ018H_bed_occupancy(self):
        """Test Xiaomi parser for MJZNZ018H bed occupancy sensor."""
        self.aeskeys = {}
        data_string = "043E29020100007b37d6d1b5cc1D020106191695fe5859db20177b37d6d1b5cc86f2d4ce0200002b6ba459CC"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "13f072b8c8469f54ac2c333ee746d771"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "MJZNZ018H"
        assert sensor_msg["mac"] == "CCB5D1D6377B"
        assert sensor_msg["packet"] == 23
        assert sensor_msg["data"]
        assert sensor_msg["bed occupancy"] == 0
        assert sensor_msg["rssi"] == -52

    def test_MJZNZ018H_double_click(self):
        """Test Xiaomi parser for MJZNZ018H double click in button."""
        self.aeskeys = {}
        data_string = "043E29020100007b37d6d1b5cc1D020106191695fe5859db20b57b37d6d1b5cceeac2cf2030000af66e6b0CC"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "13f072b8c8469f54ac2c333ee746d771"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "MJZNZ018H"
        assert sensor_msg["mac"] == "CCB5D1D6377B"
        assert sensor_msg["packet"] == 181
        assert sensor_msg["data"]
        assert sensor_msg["button"] == "double press"
        assert sensor_msg["rssi"] == -52

    def test_MJZNZ018H_battery(self):
        """Test Xiaomi parser for MJZNZ018H battery sensor."""
        self.aeskeys = {}
        data_string = "043E29020100007b37d6d1b5cc1D020106191695fe5859db200a7b37d6d1b5cce79fcf95020000a0e4f773CC"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "13f072b8c8469f54ac2c333ee746d771"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "MJZNZ018H"
        assert sensor_msg["mac"] == "CCB5D1D6377B"
        assert sensor_msg["packet"] == 10
        assert sensor_msg["data"]
        assert sensor_msg["battery"] == 76
        assert sensor_msg["rssi"] == -52

    def test_XMWXKG01LM_single_click(self):
        """Test Xiaomi parser for XMWXKG01LM single click on switch."""
        self.aeskeys = {}
        data_string = "043E28020100000d692a3cc2181C020106181695fe58598723ff0d692a3cc21876d7a70800006024e757C0"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "c533a5ab361b0a24de4d21d1d9a3d8a1"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "XMWXKG01LM"
        assert sensor_msg["mac"] == "18C23C2A690D"
        assert sensor_msg["packet"] == 255
        assert sensor_msg["data"]
        assert sensor_msg["one btn switch"] == "toggle"
        assert sensor_msg["button switch"] == "single press"
        assert sensor_msg["rssi"] == -64

    def test_XMWXKG01LM_double_click(self):
        """Test Xiaomi parser for XMWXKG01LM double click on switch."""
        self.aeskeys = {}
        data_string = "043E28020100000d692a3cc2181C020106181695fe58598723010d692a3cc218f397dd09000079826b9dC0"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "c533a5ab361b0a24de4d21d1d9a3d8a1"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "XMWXKG01LM"
        assert sensor_msg["mac"] == "18C23C2A690D"
        assert sensor_msg["packet"] == 1
        assert sensor_msg["data"]
        assert sensor_msg["one btn switch"] == "toggle"
        assert sensor_msg["button switch"] == "double press"
        assert sensor_msg["rssi"] == -64

    def test_XMWXKG01LM_long_click(self):
        """Test Xiaomi parser for XMWXKG01LM long click on switch."""
        self.aeskeys = {}
        data_string = "043E28020100000d692a3cc2181C020106181695fe58598723030d692a3cc218258824090000a360b8a1C0"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "c533a5ab361b0a24de4d21d1d9a3d8a1"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "XMWXKG01LM"
        assert sensor_msg["mac"] == "18C23C2A690D"
        assert sensor_msg["packet"] == 3
        assert sensor_msg["data"]
        assert sensor_msg["one btn switch"] == "toggle"
        assert sensor_msg["button switch"] == "long press"
        assert sensor_msg["rssi"] == -64

    def test_Xiaomi_PTX(self):
        """Test Xiaomi parser for PTX BLE wireless switch."""
        self.aeskeys = {}
        data_string = "043E2802010000adb9a538c1a41c020106181695fe5859bb3804adb9a538c1a4dc10b50400002c122fb6CC"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "a74510b40386d35ae6227a7451efc76e"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "PTX"
        assert sensor_msg["mac"] == "A4C138A5B9AD"
        assert sensor_msg["packet"] == 4
        assert sensor_msg["data"]
        assert sensor_msg["one btn switch"] == "toggle"
        assert sensor_msg["button switch"] == "single press"
        assert sensor_msg["rssi"] == -52

    def test_Xiaomi_XMPIRO2SXS(self):
        """Test Xiaomi parser for XMPIRO2SXS."""
        self.aeskeys = {}
        data_string = "043E260201000043ea2d958edc1a020106161695fe485931350b64799117331ef4020000c5d2f6acCC"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "685d647dc5e7bc9bcfcf5a1357bd2114"

        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "XMPIRO2SXS"
        assert sensor_msg["mac"] == "DC8E952DEA43"
        assert sensor_msg["packet"] == 11
        assert sensor_msg["data"]
        assert sensor_msg["motion"] == 1
        assert sensor_msg["motion timer"] == 1
        assert sensor_msg["illuminance"] == 51.0
        assert sensor_msg["rssi"] == -52
