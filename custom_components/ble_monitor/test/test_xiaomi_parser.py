"""The tests for the Xiaomi ble_parser."""
from ble_monitor.ble_parser import BleParser


class TestXiaomi:

    def test_Xiaomi_LYWSDCGQ(self):
        """Test Xiaomi parser for LYWSDCGQ."""
        data_string = "043e2502010000219335342d5819020106151695fe5020aa01da219335342d580d1004fe004802c4"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

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
        data_string = "043e2a020100005f12342d585a1e0201061a1695fe5858480b685f12342d585a0b1841e2aa000e00a4964fb5b6"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "814aac74c4f17b6c1581e1ab87816b99"
        self.aeskeys = {}

        p_mac = bytes.fromhex("5A582D34125F")
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        allow_list = self.aeskeys.keys()

        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys, discovery=False, sensor_whitelist=allow_list)
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "CGG1-ENCRYPTED"
        assert sensor_msg["mac"] == "5A582D34125F"
        assert sensor_msg["packet"] == 104
        assert sensor_msg["data"]
        assert sensor_msg["humidity"] == 59.6
        assert sensor_msg["rssi"] == -74

    def test_Xiaomi_CGDK2(self):
        """Test Xiaomi parser for CGDK2."""
        data_string = "043e2a02010000892012342d581e0201061a1695fe58586f0607892012342d585f176dd54f0200002fa453faaf"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "a3bfe9853dd85a620debe3620caaa351"
        self.aeskeys = {}
        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

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
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V3)"
        assert sensor_msg["type"] == "LYWSD03MMC"
        assert sensor_msg["mac"] == "A4C138B4944C"
        assert sensor_msg["packet"] == 3
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 27.2
        assert sensor_msg["humidity"] == 49.0
        assert sensor_msg["rssi"] == -49

    def test_Xiaomi_LYWSD03MMC_encrypted(self):
        """Test Xiaomi parser for LYWSD03MMC with encryption."""
        data_string = "043e2a02010000f4830238c1a41e0201061a1695fe58585b0550f4830238c1a495ef58763c26000097e2abb5e2"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "e9ea895fac7cca6d30532432a516f3a8"
        self.aeskeys = {}
        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "LYWSD03MMC"
        assert sensor_msg["mac"] == "A4C1380283F4"
        assert sensor_msg["packet"] == 80
        assert sensor_msg["data"]
        assert sensor_msg["humidity"] == 46.7
        assert sensor_msg["rssi"] == -30

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
        data_string = "043e2902010000bc9ce344ef541d020106191695fe5859970966bc9ce344ef5401081205000000715ebe90cb"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "5b51a7c91cde6707c9ef18dfda143a58"
        self.aeskeys = {}
        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V5 encrypted)"
        assert sensor_msg["type"] == "JTYJGD03MI"
        assert sensor_msg["mac"] == "54EF44E39CBC"
        assert sensor_msg["packet"] == 102
        assert sensor_msg["data"]
        assert sensor_msg["smoke detector"] == 1
        assert sensor_msg["rssi"] == -53

    def test_Xiaomi_JTYJGD03MI_press(self):
        """Test Xiaomi parser for JTYJGD03MI."""
        data_string = "043e2b02010000bc9ce344ef541f0201061b1695fe5859970964bc9ce344ef5422206088fd000000003a148fb3cb"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "5b51a7c91cde6707c9ef18dfda143a58"
        self.aeskeys = {}
        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

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
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

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
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

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

    def test_Xiaomi_MJYD02YL(self):
        """Test Xiaomi parser for MJYD02YL."""

    def test_Xiaomi_MUE4094RT(self):
        """Test Xiaomi parser for MUE4094RT."""
        data_string = "043e1c020102010c39b2e870de100201060c1695fe4030dd032403000101c6"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

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
        data_string = "043e2b020103000fc4e044ef541f0201061b1695fe58598d0a170fc4e044ef547cc27a5c03a1000000790df258bb"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "FFD8CE9C08AE7533A79BDAF0BB755E96"
        self.aeskeys = {}
        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

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
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V2)"
        assert sensor_msg["type"] == "MMC-T201-1"
        assert sensor_msg["mac"] == "0081F9DD6FC1"
        assert sensor_msg["packet"] == 111
        assert sensor_msg["data"]
        assert sensor_msg["temperature"] == 36.87199806168224
        assert sensor_msg["battery"] == 81
        assert sensor_msg["rssi"] == -79

    def test_Xiaomi_M1S_T500(self):
        """Test Xiaomi parser for M1S-T500."""
        data_string = "043e2402010001115b174371e618020106141695fe7130890437115b174371e6091000020003dc"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V3)"
        assert sensor_msg["type"] == "M1S-T500"
        assert sensor_msg["mac"] == "E67143175B11"
        assert sensor_msg["packet"] == 55
        assert sensor_msg["data"]
        assert sensor_msg["toothbrush"] == 1
        assert sensor_msg["counter"] == 3
        assert sensor_msg["rssi"] == -36

    def test_Xiaomi_ZNMS16LM_fingerprint(self):
        """Test Xiaomi parser for ZNMS16LM."""
        data_string = "043e2a02010000918aeb441fd71e020106030295fe161695fe50449e0642918aeb441fd7060005ffffffff00a9"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

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
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V4)"
        assert sensor_msg["type"] == "ZNMS16LM"
        assert sensor_msg["mac"] == "D71F44EB8A91"
        assert sensor_msg["packet"] == 67
        assert sensor_msg["data"]
        assert sensor_msg["lock"] == 0
        assert sensor_msg["action"] == "unlock outside the door"
        assert sensor_msg["method"] == "biometrics"
        assert sensor_msg["error"] is None
        assert sensor_msg["key id"] == 2
        assert sensor_msg["rssi"] == -87

    def test_Xiaomi_YLAI003(self):
        """Test Xiaomi parser for YLAI003."""

    def test_Xiaomi_YLYK01YL(self):
        """Test Xiaomi parser for YLYK01YL."""
        data_string = "043E21020103007450E94124F815141695FE503053013F7450E94124F8011003000000E0"
        data = bytes(bytearray.fromhex(data_string))

        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

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
        data_string = "043E25020103008B98C54124F819181695FE5830B603D28B98C54124F8C3491476757E00000099DE"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "b853075158487ca39a5b5ea9"
        self.aeskeys = {}
        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V3 encrypted)"
        assert sensor_msg["type"] == "YLKG07YL/YLKG08YL"
        assert sensor_msg["mac"] == "F82441C5988B"
        assert sensor_msg["packet"] == 210
        assert sensor_msg["data"]
        assert sensor_msg["dimmer"] == 1
        assert sensor_msg["button"] == "short press"
        assert sensor_msg["rssi"] == -34

    def test_Xiaomi_YLKG07YL_rotate(self):
        """Test Xiaomi parser for YLKG07YL, YLKG08YL while rotating dimmer."""
        data_string = "043e25020103008b98c54124f819181695fe5830b603368b98c54124f88bb8f2661351000000d6ef"
        data = bytes(bytearray.fromhex(data_string))

        aeskey = "b853075158487ca39a5b5ea9"
        self.aeskeys = {}
        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        mac_address = mac.hex()
        p_mac = bytes.fromhex(mac_address.replace(":", "").lower())
        p_key = bytes.fromhex(aeskey.lower())
        self.aeskeys[p_mac] = p_key
        # pylint: disable=unused-variable
        ble_parser = BleParser(aeskeys=self.aeskeys)
        sensor_msg, tracker_msg = ble_parser.parse_data(data)

        assert sensor_msg["firmware"] == "Xiaomi (MiBeacon V3 encrypted)"
        assert sensor_msg["type"] == "YLKG07YL/YLKG08YL"
        assert sensor_msg["mac"] == "F82441C5988B"
        assert sensor_msg["packet"] == 54
        assert sensor_msg["data"]
        assert sensor_msg["dimmer"] == 1
        assert sensor_msg["button"] == "rotate left"
        assert sensor_msg["rssi"] == -17

    def test_Xiaomi_K9B(self):
        """Test Xiaomi parser for K9B."""
