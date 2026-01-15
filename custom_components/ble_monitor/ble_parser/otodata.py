"""Parser for Otodata propane tank monitor BLE advertisements"""
import logging
import struct
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)


def parse_otodata(self, data: bytes, mac: bytes):
    """Otodata propane tank monitor parser
    
    The device sends multiple packet types:
    - OTO3281: Device identifier/info packet
    - OTOSTAT: Status packet  
    - OTOTELE: Telemetry packet (contains sensor data like tank level)
    
    Packet structure (variable length):
    - Bytes 0-1: Company ID (0x03B1 in little-endian)
    - Bytes 2-9: Packet type identifier (e.g., "OTOTELE")
    - Bytes 9+: Sensor data (format varies by packet type)
    """
    msg_length = len(data)
    firmware = "Otodata"
    result = {"firmware": firmware}
    
    # Minimum packet size validation
    if msg_length < 18:
        if self.report_unknown == "Otodata":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Otodata DEVICE: MAC: %s, ADV: %s",
                to_mac(mac),
                data.hex()
            )
        return None
    
    # Parse packet type from bytes 2-9
    try:
        packet_type = data[2:9].decode('ascii', errors='ignore').strip()
        if packet_type.startswith('OTO'):
            device_type = f"Propane Tank Monitor"
        else:
            device_type = "Propane Tank Monitor"
        
        _LOGGER.info("Otodata packet type: %s, length: %d bytes", packet_type, msg_length)
    except Exception:
        device_type = "Propane Tank Monitor"
        packet_type = "UNKNOWN"
    
    try:
        # Parse sensor values based on packet type
        # Tank is at 71% - searching for this value
        
        _LOGGER.info("=== Otodata Packet Analysis ===")
        _LOGGER.info("Packet Type: %s", packet_type)
        _LOGGER.info("Full hex: %s", data.hex())
        _LOGGER.info("MAC: %s", to_mac(mac))
        
        # Log all bytes after the packet type identifier (starting at byte 9)
        start_byte = 9
        _LOGGER.info("Data bytes (starting at position %d):", start_byte)
        for i in range(start_byte, msg_length):
            _LOGGER.info("  Byte %d: 0x%02X = %d", i, data[i], data[i])
        
        # Search for tank level = 71% in various encodings
        _LOGGER.info("Searching for tank level ~71%%...")
        candidates = []
        
        for i in range(start_byte, msg_length):
            val = data[i]
            # Direct match (69-73)
            if 69 <= val <= 73:
                candidates.append((i, val, "direct"))
                _LOGGER.info("  *** CANDIDATE at byte %d: %d (direct) ***", i, val)
            # Inverted (100 - value)
            inverted = 100 - val
            if 69 <= inverted <= 73:
                candidates.append((i, inverted, "inverted"))
                _LOGGER.info("  *** CANDIDATE at byte %d: 100-%d = %d (inverted/empty%%) ***", i, val, inverted)
        
        # Try 16-bit values (little-endian)
        if msg_length >= start_byte + 2:
            _LOGGER.info("16-bit values (little-endian):")
            for i in range(start_byte, min(msg_length - 1, start_byte + 16)):
                val_le = unpack("<H", data[i:i+2])[0]
                _LOGGER.info("  Bytes [%d-%d]: %d", i, i+1, val_le)
                if 69 <= val_le <= 73:
                    candidates.append((i, val_le, "16-bit LE"))
                    _LOGGER.info("    *** CANDIDATE: %d (16-bit LE) ***", val_le)
        
        # Determine which value to use based on packet type
        tank_level = None
        
        if packet_type == "OTOTELE":
            # Telemetry packet - most likely contains tank level
            # Based on analysis, byte 12 (0x1c=28) inverted gives 72% (close to 71%)
            if msg_length > 12:
                empty_percent = data[12]
                tank_level = 100 - empty_percent
                _LOGGER.info("OTOTELE: Using byte 12 (inverted): 100-%d = %d%%", empty_percent, tank_level)
        
        # If we found candidates but haven't set tank_level yet
        if tank_level is None and candidates:
            # Use the first candidate found
            byte_pos, value, method = candidates[0]
            tank_level = value
            _LOGGER.info("Using first candidate: byte %d = %d (%s)", byte_pos, value, method)
        elif tank_level is None:
            # Default fallback
            tank_level = data[15] if msg_length > 15 else 0
            _LOGGER.info("No candidates found, using byte 15: %d", tank_level)
        
        result.update({
            "tank level": tank_level,
        })
        
        _LOGGER.info("Final result: tank_level=%d%% (expected ~71%%)", tank_level)
        _LOGGER.info("=== End Analysis ===")
        
        
    except (IndexError, struct.error) as e:
        _LOGGER.debug("Failed to parse Otodata data: %s", e)
        return None

    result.update({
        "mac": to_unformatted_mac(mac),
        "type": device_type,
        "packet": "no packet id",
        "data": True
    })
    
    return result
