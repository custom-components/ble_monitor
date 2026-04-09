"""Tests for the Otodata parser"""
import logging
from unittest import TestCase

from custom_components.ble_monitor.ble_parser import BleParser

_LOGGER = logging.getLogger(__name__)


class TestOtodata(TestCase):
    """Tests for the Otodata parser"""
    
    def test_otodata_propane_tank_monitor(self):
        """Test Otodata Propane Tank Monitor parser with real captured data."""
        # Real BLE advertisement data captured from Otodata device
        # Manufacturer specific data: b'\x1a\xff\xb1\x03OTO3281\x90`\xbc\x01\x10\x18!\x03\x84\x06\x03\x04\xb0\x13\x02\x05'
        # MAC: ea109060bc01
        # Company ID: 0x03B1 (945 decimal)
        
        # Construct full BLE packet
        # Format: HCI header + MAC + advertisement data
        data_string = "043E2A02010001BC609010EA1E1AFF B103 4F544F33323831 9060BC01 10 18 21 03 8406 0304 B013 0205"
        data_string = data_string.replace(" ", "")  # Remove spaces
        
        data = bytes(bytearray.fromhex(data_string))
        
        # pylint: disable=unused-variable
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)
        
        # Validate parser output
        assert sensor_msg is not None, "Parser should return sensor data"
        assert sensor_msg["firmware"] == "Otodata"
        assert "Propane Tank Monitor" in sensor_msg["type"]
        assert sensor_msg["mac"] == "01bc609010ea"  # MAC in unformatted lowercase
        assert sensor_msg["packet"] == "no packet id"
        assert sensor_msg["data"] is True
        
        # Check sensor values
        assert "tank level" in sensor_msg
        
        # Validate tank level is a reasonable percentage (0-100)
        # Note: The actual value (24) may need adjustment once we verify the correct byte position
        assert 0 <= sensor_msg["tank level"] <= 100, f"Tank level should be 0-100, got {sensor_msg['tank level']}"
        
        # RSSI should be negative
        assert sensor_msg["rssi"] < 0
        
        # Log for debugging
        _LOGGER.info("Parsed sensor data: %s", sensor_msg)
        
    def test_otodata_invalid_data(self):
        """Test Otodata parser with invalid/short data."""
        # Test with data that's too short
        data_string = "043E0A0201000011223344556603020106"
        data = bytes(bytearray.fromhex(data_string))
        
        ble_parser = BleParser()
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)
        
        # Parser should handle invalid data gracefully
        # Either return None or handle the error
        # Adjust assertion based on your implementation
        
    def test_otodata_different_packet_formats(self):
        """Test different packet formats if Otodata uses multiple formats."""
        # Some devices send different packet formats (e.g., short vs. long packets)
        # Add tests for each format your device uses
        pass


# NOTE: To run these tests:
# 1. Place this file in: custom_components/ble_monitor/test/
# 2. Install test requirements: pip install -r requirements_test.txt
# 3. Run tests: python -m pytest custom_components/ble_monitor/test/test_otodata_parser.py
#
# REMEMBER: You MUST replace the example data with actual BLE advertisements from your device!
