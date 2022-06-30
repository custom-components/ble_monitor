"""Parser for HA BLE (DIY sensors) advertisements"""
import logging
import struct
from Cryptodome.Cipher import AES

from .helpers import (
    to_mac,
    to_unformatted_mac,
)

_LOGGER = logging.getLogger(__name__)


def parse_uint(data_obj, factor=1):
    """convert bytes (as unsigned integer) and factor to float"""
    decimal_places = -int(f'{factor:e}'.split('e')[-1])
    return round(int.from_bytes(data_obj, "little", signed=False) * factor, decimal_places)


def parse_int(data_obj, factor=1):
    """convert bytes (as signed integer) and factor to float"""
    decimal_places = -int(f'{factor:e}'.split('e')[-1])
    return round(int.from_bytes(data_obj, "little", signed=True) * factor, decimal_places)


def parse_float(data_obj, factor=1):
    """convert bytes (as float) and factor to float"""
    decimal_places = -int(f'{factor:e}'.split('e')[-1])
    if len(data_obj) == 2:
        [val] = struct.unpack('e', data_obj)
    if len(data_obj) == 4:
        [val] = struct.unpack('f', data_obj)
    elif len(data_obj) == 8:
        [val] = struct.unpack('d', data_obj)
    else:
        _LOGGER.error("only 2, 4 or 8 byte long floats are supported in HA BLE")
        return None
    return round(val * factor, decimal_places)


def parse_string(data_obj, factor=None):
    """convert bytes to string"""
    return data_obj.decode('UTF-8')


def parse_mac(data_obj):
    """convert bytes to mac"""
    if len(data_obj) == 6:
        return data_obj[::-1]
    else:
        _LOGGER.error("MAC address has to be 6 bytes long")
        return None


dispatch = {
    0x00: parse_uint,
    0x01: parse_int,
    0x02: parse_float,
    0x03: parse_string,
    0x04: parse_mac,
}

DATA_MEAS_DICT = {
    0x00: ["packet", 1],
    0x01: ["battery", 1],
    0x02: ["temperature", 0.01],
    0x03: ["humidity", 0.01],
    0x04: ["pressure", 0.01],
    0x05: ["illuminance", 0.01],
    0x06: ["weight", 0.01],
    0x07: ["weight unit", None],
    0x08: ["dewpoint", 0.01],
    0x09: ["count", 1],
    0x0A: ["energy", 0.001],
    0x0B: ["power", 0.01],
    0x0C: ["voltage", 0.001],
    0x0D: ["pm2.5", 1],
    0x0E: ["pm10", 1],
    0x0F: ["binary", 1],
    0x10: ["switch", 1],
    0x11: ["opening", 1],
    0x12: ["co2", 1],
    0x13: ["tvoc", 1],
}


def parse_ha_ble(self, data, uuid16, source_mac, rssi):
    """Home Assistant BLE parser"""
    device_type = "HA BLE DIY"
    ha_ble_mac = source_mac
    result = {}
    packet_id = None

    if uuid16 == 0x181C:
        # Non-encrypted HA BLE format
        payload = data[4:]
        firmware = "HA BLE"
        packet_id = None
    elif uuid16 == 0x181E:
        # Encrypted HA BLE format
        try:
            payload, count_id = decrypt_data(self, data, ha_ble_mac)
        except TypeError:
            return None
        firmware = "HA BLE (encrypted)"
        if count_id:
            packet_id = parse_uint(count_id)
    else:
        return None

    if payload:
        payload_length = len(payload)
        payload_start = 0
    else:
        return None

    payload_length = len(payload)
    payload_start = 0

    while payload_length >= payload_start + 1:
        obj_control_byte = payload[payload_start]
        obj_data_length = (obj_control_byte >> 0) & 31  # 5 bits (0-4)
        obj_data_format = (obj_control_byte >> 5) & 7  # 3 bits (5-7)
        obj_meas_type = payload[payload_start + 1]
        next_start = payload_start + 1 + obj_data_length
        if payload_length < next_start:
            _LOGGER.debug("Invalid payload data length, payload: %s", payload.hex())
            break

        if obj_data_length != 0:
            if obj_data_format <= 3:
                if obj_meas_type in DATA_MEAS_DICT:
                    meas_data = payload[payload_start + 2:next_start]
                    meas_type = DATA_MEAS_DICT[obj_meas_type][0]
                    meas_factor = DATA_MEAS_DICT[obj_meas_type][1]
                    meas = dispatch[obj_data_format](meas_data, meas_factor)
                    result.update({meas_type: meas})
                else:
                    if self.report_unknown == "HA BLE":
                        _LOGGER.error("UNKNOWN dataobject in HA BLE payload! Adv: %s", data.hex())
            elif obj_data_format == 4:
                data_mac = dispatch[obj_data_format](payload[payload_start + 1:next_start])
                if data_mac:
                    ha_ble_mac = data_mac
            else:
                if self.report_unknown == "HA BLE":
                    _LOGGER.error("UNKNOWN dataobject in HA BLE payload! Adv: %s", data.hex())
        payload_start = next_start

    if not result:
        if self.report_unknown == "HA BLE":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Home Assistant BLE DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # Check for packet id in payload
    if result.get("packet"):
        packet_id = result["packet"]

    # Check for duplicate messages
    if packet_id:
        try:
            prev_packet = self.lpacket_ids[ha_ble_mac]
        except KeyError:
            # start with empty first packet
            prev_packet = None
        if prev_packet == packet_id:
            # only process new messages
            if self.filter_duplicates is True:
                return None
        self.lpacket_ids[ha_ble_mac] = packet_id
    else:
        packet_id = "no packet id"

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and ha_ble_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(ha_ble_mac))
        return None

    result.update({
        "rssi": rssi,
        "mac": to_unformatted_mac(ha_ble_mac),
        "packet": packet_id,
        "type": device_type,
        "firmware": firmware,
        "data": True
    })
    return result


def decrypt_data(self, data, ha_ble_mac):
    """Decrypt encrypted HA BLE advertisements"""
    # check for minimum length of encrypted advertisement
    if len(data) < 15:
        _LOGGER.debug("Invalid data length (for decryption), adv: %s", data.hex())
    # try to find encryption key for current device
    try:
        key = self.aeskeys[ha_ble_mac]
        if len(key) != 16:
            _LOGGER.error("Encryption key should be 16 bytes (32 characters) long")
            return None, None
    except KeyError:
        # no encryption key found
        _LOGGER.error("No encryption key found for device with MAC %s", to_mac(ha_ble_mac))
        return None, None
    uuid = data[2:4]
    encrypted_payload = data[4:-8]
    count_id = data[-8:-4]
    mic = data[-4:]

    # nonce: mac [6], uuid16 [2], count_id [4] (6+2+4 = 12 bytes)
    nonce = b"".join([ha_ble_mac, uuid, count_id])
    cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
    cipher.update(b"\x11")
    try:
        decrypted_payload = cipher.decrypt_and_verify(encrypted_payload, mic)
    except ValueError as error:
        _LOGGER.warning("Decryption failed: %s", error)
        _LOGGER.debug("mic: %s", mic.hex())
        _LOGGER.debug("nonce: %s", nonce.hex())
        _LOGGER.debug("encrypted_payload: %s", encrypted_payload.hex())
        return None
    if decrypted_payload is None:
        _LOGGER.error(
            "Decryption failed for %s, decrypted payload is None",
            to_mac(ha_ble_mac),
        )
        return None, None
    return decrypted_payload, count_id
