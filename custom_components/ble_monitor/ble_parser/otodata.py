"""Parser for Otodata propane tank monitor BLE advertisements"""
import logging
from struct import unpack

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)

# Cache device attributes from OTO3281 packets to use in OTOTELE packets
_device_cache = {}


def parse_otodata(self, data: bytes, mac: bytes):
    """Otodata propane tank monitor parser
    
    The device sends multiple packet types:
    - OTO3281: Device identifier/info packet
    - OTOSTAT: Status packet  
    - OTOTELE: Telemetry packet (contains sensor data like tank level)
    
    Packet structure (man_spec_data format):
    - Byte 0: Data length
    - Byte 1: Type flag (0xFF)
    - Bytes 2-3: Company ID (0x03B1 little-endian: \xb1\x03)
    - Bytes 4-10: Packet type identifier (7 chars, e.g., "OTOTELE")
    - Bytes 11+: Sensor data (format varies by packet type)
    """
    msg_length = len(data)
    firmware = "Otodata"
    result = {"firmware": firmware}
    
    _LOGGER.debug("Otodata parse_otodata called - length=%d", msg_length)
    
    # Minimum packet size validation
    if msg_length < 18:
        if self.report_unknown == "Otodata":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Otodata DEVICE: MAC: %s, ADV: %s",
                to_mac(mac),
                data.hex()
            )
        return None
    
    # Parse packet type from man_spec_data
    # Byte 0: length, Byte 1: type flag, Bytes 2-3: company ID
    # Bytes 4-10 contain the 7-character packet type (OTO3281, OTOSTAT, OTOTELE)
    # Bytes 11+: Sensor data
    try:
        packet_type = data[4:11].decode('ascii', errors='ignore').strip()
        _LOGGER.debug("Otodata packet_type: %s", packet_type)
        if packet_type.startswith('OTO'):
            device_type = f"Propane Tank Monitor"
        else:
            device_type = "Propane Tank Monitor"
        
        _LOGGER.debug("Otodata packet type: '%s', length: %d bytes", packet_type, msg_length)
    except Exception:
        device_type = "Propane Tank Monitor"
        packet_type = "UNKNOWN"
    
    try:
        # Parse different packet types
        # Three packet types observed:
        # - OTO3281 or OTO32##: Device identifier/info
        # - OTOSTAT: Status information  
        # - OTOTELE: Telemetry data (primary sensor readings)
        
        _LOGGER.debug("Processing %s packet (length: %d)", packet_type, msg_length)
        
        # Parse based on packet type
        if packet_type == "OTOTELE":
            # Telemetry packet - tank level is a 2-byte little-endian value at bytes 9-10 (percentage * 100)
            if msg_length < 15:
                _LOGGER.warning("OTOTELE packet too short: %d bytes", msg_length)
                return None

            tank_level_raw = int.from_bytes(data[9:11], byteorder="little")
            tank_level = tank_level_raw / 100.0
            _LOGGER.debug("OTOTELE: tank_level_raw=%d, tank_level=%.2f%%", tank_level_raw, tank_level)

            result.update({
                "tank level": tank_level,
            })

            # Add cached device attributes if available
            mac_str = to_unformatted_mac(mac)
            if mac_str in _device_cache:
                result.update(_device_cache[mac_str])
            
        elif packet_type == "OTOSTAT":
            # Status packet - contains unknown device status values
            # Byte 12: Incrementing value (purpose unknown)
            # Byte 13: Constant 0x06 (purpose unknown)
            # Until we identify what these represent, we skip this packet type
            
            _LOGGER.debug("OTOSTAT packet received - skipping (unknown data format)")
            
            # Skip OTOSTAT - unknown data format
            return None
            
        elif packet_type.startswith("OTO3") or packet_type.startswith("OTO32"):
            # Device info packet - contains product info and serial number
            # Example: 1affb1034f544f333238319060bc011018210384060304b0130205
            # Bytes 4-10: "OTO3281" - packet type identifier
            # Bytes 20-21: Model number (e.g., 0x13B0 = 5040 for TM5040)
            
            if msg_length < 22:
                _LOGGER.warning("OTO3xxx packet too short: %d bytes", msg_length)
                return None
            
            # Extract model number from bytes 20-21 (little-endian)
            # Full model format: MT4AD-TM5040 (5040 from bytes 20-21)
            if msg_length >= 22:
                model_number = unpack("<H", data[20:22])[0]
                product_name = f"MT4AD-TM{model_number}"
            else:
                product_name = packet_type[3:] if len(packet_type) > 3 else "Unknown"
            
            # Cache device attributes to add to future OTOTELE packets
            mac_str = to_unformatted_mac(mac)
            _device_cache[mac_str] = {
                "product": f"Otodata {product_name}",
                "model": product_name,
            }
            
            _LOGGER.info("Otodata device detected - Model: %s, MAC: %s", 
                        product_name, to_mac(mac))
            
            # Don't create sensor entities for device info packets
            return None
            
        else:
            _LOGGER.warning("Unknown Otodata packet type: %s", packet_type)
            return None
        
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
