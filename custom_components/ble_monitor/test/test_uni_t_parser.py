import unittest
from custom_components.ble_monitor.ble_parser.uni_t import parse_uni_t
from custom_components.ble_monitor.ble_parser import BleParser
import logging

# Configure logging to capture debug messages for the test
# This basicConfig is for the test environment. The actual component might have its own logging setup.
logger = logging.getLogger("custom_components.ble_monitor.ble_parser.uni_t")
logger.setLevel(logging.DEBUG)
# Adding a handler if no handlers are configured (e.g., when running tests directly)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.DEBUG)


class TestUniTParser(unittest.TestCase):

    def test_uni_t_ut363bt_valid_data(self):
        # Simulates the BleParser class or necessary parts of it for the test
        # In a real scenario, this might be a mock object or a minimal BleParser instance
        parser_self = BleParser(report_unknown=False, discovery=True, filter_duplicates=False)
        parser_self.rssi = -70 # Example RSSI

        # Sample data construction:
        # mfg[0] = 0x14 (data_len = 20 for type+compid+payload)
        # Total length of mfg array is mfg[0]+1 = 21 bytes.
        # mfg[1] = 0xFF (type)
        # mfg[2:4] = 0xAABB (CompID: LSB AA, MSB BB -> comp_id value 0xBBAA)
        #           comp_id = (mfg[3] << 8) | mfg[2] -> (0xBB << 8) | 0xAA = 0xBBAA
        # pkt = mfg[3] -> 0xBB
        # mfg[4] = 0x00 (skipped byte in current uni_t parser logic for txt)
        # mfg[5:16] = "  2.75M/S50" (wind speed 2.75, unit code 50 = km/h) (11 bytes)
        #             Hex: 2020322E37354D2F533530
        # mfg[16:18] = Temperature 28.3°C (sent as 283, little endian: 1B 01) (2 bytes)
        # mfg[18:21] = Padding (0x000000) (3 bytes for a total of 17 payload bytes)
        
        mfg_data_hex = "14ffaabb002020322e37354d2f5335301b01000000" 
        mfg_bytes = bytes.fromhex(mfg_data_hex)
        mac_bytes = bytes.fromhex("112233445566")

        # Capture logs specifically from the uni_t parser's logger
        with self.assertLogs(logger='custom_components.ble_monitor.ble_parser.uni_t', level='DEBUG') as log_watcher:
            data = parse_uni_t(parser_self, mfg_bytes, mac_bytes)

        self.assertIsNotNone(data)
        self.assertEqual(data["type"], "UNI‑T")
        self.assertEqual(data["firmware"], "UT363BT")
        self.assertEqual(data["mac"], "112233445566")
        
        # Wind speed: 2.75 km/h. Factor for km/h (uc 50) is 1/3.6
        # Expected speed in m/s = 2.75 / 3.6 = 0.763888...
        self.assertAlmostEqual(data["wind_speed"], 2.75 / 3.6, places=2) 
        
        # Temperature: 283 / 10.0 = 28.3
        self.assertEqual(data["temperature"], 28.3)
        
        self.assertEqual(data["packet"], 0xBB) # mfg[3] is 0xBB
        self.assertTrue(data["data"])
        self.assertEqual(data["rssi"], -70)

        # Check for the debug log message
        # The log message includes the hex string WITHOUT "0x" prefix for each byte, and is lower case.
        expected_log_payload = mfg_data_hex # The mfg.hex() produces lowercase without 0x
        self.assertTrue(any(f"UNI-T raw mfg data: {expected_log_payload}" in msg for msg in log_watcher.output),
                        f"Expected log message not found in {log_watcher.output}")

    def test_uni_t_invalid_data_short(self):
        parser_self = BleParser(report_unknown=False, discovery=True, filter_duplicates=False)
        parser_self.rssi = -70
        # mfg[0] = 0x10 (16), so total length 17. Payload is 16-1-2=13 bytes.
        # String slice mfg[5:16] will be 11 bytes. Temp slice mfg[16:18] will be out of bounds.
        mfg_bytes = bytes.fromhex("10ffaabb002020322e37354d") # Too short for temp parsing
        mac_bytes = bytes.fromhex("112233445566")
        data = parse_uni_t(parser_self, mfg_bytes, mac_bytes)
        self.assertIsNone(data)

    def test_uni_t_string_decode_error_or_format(self):
        # Test if string parsing fails gracefully due to bad format (no M/S)
        parser_self = BleParser(report_unknown=False, discovery=True, filter_duplicates=False)
        parser_self.rssi = -70
        # Valid length, but speed string part does not contain "M/S"
        mfg_data_hex = "14ffaabb002020322e373520202020201b01000000" # "  2.75      " instead of M/S
        mfg_bytes = bytes.fromhex(mfg_data_hex)
        mac_bytes = bytes.fromhex("112233445566")
        data = parse_uni_t(parser_self, mfg_bytes, mac_bytes)
        self.assertIsNone(data)

    def test_uni_t_temp_parse_error(self):
        # Test if temperature parsing fails due to insufficient bytes after string
        # String mfg[5:16] uses up to index 15. Temperature needs mfg[16] and mfg[17].
        # If mfg[0] implies total length is too short for mfg[17]
        parser_self = BleParser(report_unknown=False, discovery=True, filter_duplicates=False)
        parser_self.rssi = -70
        # mfg[0] = 0x13 (19). Total length 20. Payload 19-1-2 = 16 bytes.
        # Payload mfg[4]...mfg[19].
        # String mfg[5:16] (11 bytes) is fine (mfg[5]..mfg[15]).
        # Temp mfg[16:18] needs mfg[16] and mfg[17]. This is fine.
        # Let's make it one byte shorter: mfg[0] = 0x12 (18). Total length 19. Payload 15 bytes.
        # Payload mfg[4]..mfg[18].
        # String mfg[5:16] (11 bytes) is fine. (mfg[5]..mfg[15])
        # Temp mfg[16:18] needs mfg[16], mfg[17]. mfg[17] is available.
        # This should still work. What if mfg[0] = 0x11 (17). Total 18. Payload 14.
        # Payload mfg[4]..mfg[17]. String mfg[5:16] fine. Temp mfg[16:18] needs mfg[16], mfg[17]. mfg[17] is available.
        # The error is when mfg[16:18] slice itself is too short.
        # This means len(mfg) must be at least 18.
        # If mfg_bytes = bytes.fromhex("14ffaabb002020322e37354d2f5335301b") # Missing one byte for temp (total 20 bytes, mfg[0]=0x14)
        # This will cause an error because `mfg[16:18]` will be shorter than 2 bytes if len(mfg) is 17, but here len(mfg) is 20.
        # The check for `data_len == 0x14` is in `__init__`. The parser itself doesn't recheck length.
        # The try-except in `parse_uni_t` should catch index errors.
        
        # This mfg_data has mfg[0]=0x14, so it's 21 bytes long.
        # Slicing mfg[16:18] is fine. Error would be if mfg itself is too short.
        # e.g. mfg_bytes is actually shorter than 18 bytes.
        mfg_short_for_temp = bytes.fromhex("14ffaabb002020322e37354d2f5335301b") # Only 1 byte for temp
        # This construction is faulty. The first byte 0x14 dictates expected length of 21.
        # The test should be that the actual mfg_bytes is too short.
        
        mfg_bytes_actually_short = bytes.fromhex("AABBCCDDEEFF00112233445566778899AA") # 17 bytes long
        # This will fail int.from_bytes(mfg[16:18]... if mfg is only 17 bytes long, mfg[16] is last byte, mfg[17] is OOB.
        
        mac_bytes = bytes.fromhex("112233445566")
        data = parse_uni_t(parser_self, mfg_bytes_actually_short, mac_bytes)
        self.assertIsNone(data)

if __name__ == '__main__':
    unittest.main()
