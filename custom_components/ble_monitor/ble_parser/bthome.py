"""Parser for BTHome (DIY sensors) advertisements"""
import logging
import struct
from typing import Any
from Cryptodome.Cipher import AES

from .bthome_const import MEAS_TYPES
from .helpers import (
    to_mac,
    to_unformatted_mac,
)

_LOGGER = logging.getLogger(__name__)


def parse_uint(data_obj: bytes, factor: float = 1.0) -> float:
    """Convert bytes (as unsigned integer) and factor to float."""
    decimal_places = -int(f"{factor:e}".split("e")[-1])
    return round(
        int.from_bytes(data_obj, "little", signed=False) * factor, decimal_places
    )


def parse_int(data_obj: bytes, factor: float = 1.0) -> float:
    """Convert bytes (as signed integer) and factor to float."""
    decimal_places = -int(f"{factor:e}".split("e")[-1])
    return round(
        int.from_bytes(data_obj, "little", signed=True) * factor, decimal_places
    )


def parse_float(data_obj: bytes, factor: float = 1.0):
    """Convert bytes (as float) and factor to float."""
    decimal_places = -int(f"{factor:e}".split("e")[-1])
    if len(data_obj) == 2:
        [val] = struct.unpack("e", data_obj)
    elif len(data_obj) == 4:
        [val] = struct.unpack("f", data_obj)
    elif len(data_obj) == 8:
        [val] = struct.unpack("d", data_obj)
    else:
        _LOGGER.error("only 2, 4 or 8 byte long floats are supported in BTHome BLE")
        return None
    return round(val * factor, decimal_places)


def parse_string(data_obj: bytes) -> str:
    """Convert bytes to string."""
    return data_obj.decode("UTF-8")


dispatch = {
    0x00: parse_uint,
    0x01: parse_int,
    0x02: parse_float,
    0x03: parse_string,
}


def parse_bthome(self, data, uuid16, source_mac, rssi):
    """BTHome BLE parser"""
    self.uuid16 = uuid16
    self.bthome_mac = source_mac
    self.rssi = rssi

    if self.uuid16 == 0xFCD2:
        # BTHome V2 format
        return parse_bthome_v2(self, data)
    elif self.uuid16 in [0x181C, 0x181E]:
        # BTHome V1 format
        return parse_bthome_v1(self, data)
    else:
        return None


def parse_bthome_v1(self, data):
    "Parse data in BTHome V1 format"
    self.device_type = "BTHome"
    self.packet_id = None
    sw_version = 1
    payload = data[4:]
    if self.uuid16 == 0x181C:
        # Non-encrypted BTHome V1 format
        self.firmware = "BTHome V1"
        self.packet_id = None
    elif self.uuid16 == 0x181E:
        # Encrypted BTHome V1 format
        self.firmware = "BTHome V1 (encrypted)"
        try:
            payload, count_id = decrypt_data(self, payload, sw_version)
        except (ValueError, TypeError):
            return None

        self.packet_id = parse_uint(count_id)
    else:
        return None

    return parse_payload(self, payload, sw_version)


def parse_bthome_v2(self, data):
    "Parse data in BTHome V2 format"
    self.device_type = "BTHome"
    self.packet_id = None

    adv_info = data[4]

    # Determine if encryption is used and check BTHome version
    encryption = adv_info & (1 << 0)  # bit 0
    sw_version = (adv_info >> 5) & 7  # 3 bits (5-7)
    if sw_version == 2:
        if encryption == 1:
            self.firmware = f"BTHome V{sw_version} (encrypted)"
        else:
            self.firmware = f"BTHome V{sw_version}"
    else:
        _LOGGER.error(
            "Sensor is set to use BTHome version %s, which is not existing. "
            "Please modify the version in the first byte of the service data",
            sw_version,
        )
        return False

    payload = data[5:]

    if encryption == 1:
        try:
            payload, count_id = decrypt_data(self, payload, sw_version)
        except (ValueError, TypeError):
            return None

        self.packet_id = parse_uint(count_id)

    return parse_payload(self, payload, sw_version)


def parse_payload(self, payload, sw_version):
    "Parse the payload"
    payload_length = len(payload)
    next_obj_start = 0
    prev_obj_meas_type = 0
    result = {}
    measurements: list[dict[str, Any]] = []
    postfix_dict: dict[int, int] = {}
    obj_data_format: str | int

    # Create a list with all individual objects
    while payload_length >= next_obj_start + 1:
        obj_start = next_obj_start

        if sw_version == 1:
            # BTHome V1
            obj_meas_type = payload[obj_start + 1]
            obj_data_unit = MEAS_TYPES[obj_meas_type].unit_of_measurement
            obj_control_byte = payload[obj_start]
            obj_data_length = (obj_control_byte >> 0) & 31  # 5 bits (0-4)
            obj_data_format = (obj_control_byte >> 5) & 7  # 3 bits (5-7)
            obj_data_start = obj_start + 2
            next_obj_start = obj_start + obj_data_length + 1
        else:
            # BTHome V2
            obj_meas_type = payload[obj_start]
            if prev_obj_meas_type > obj_meas_type:
                _LOGGER.warning(
                    "BTHome device is not sending object ids in numerical order (from low to "
                    "high object id). This can cause issues with your BTHome receiver, "
                    "payload: %s",
                    payload.hex(),
                )
            if obj_meas_type not in MEAS_TYPES:
                _LOGGER.debug(
                    "Invalid Object ID found in payload: %s",
                    payload.hex(),
                )
                break
            prev_obj_meas_type = obj_meas_type
            obj_data_length = MEAS_TYPES[obj_meas_type].data_length
            obj_data_format = MEAS_TYPES[obj_meas_type].data_format
            obj_data_unit = MEAS_TYPES[obj_meas_type].unit_of_measurement
            obj_data_start = obj_start + 1
            next_obj_start = obj_start + obj_data_length + 1

        if obj_data_length == 0:
            _LOGGER.debug(
                "Invalid payload data length found with length 0, payload: %s",
                payload.hex(),
            )
            continue

        if payload_length < next_obj_start:
            _LOGGER.debug("Invalid payload data length, payload: %s", payload.hex())
            break
        measurements.append(
            {
                "data format": obj_data_format,
                "data unit": obj_data_unit,
                "data length": obj_data_length,
                "measurement type": obj_meas_type,
                "measurement data": payload[obj_data_start:next_obj_start],
                "device id": None,
            }
        )

    # Get a list of measurement types that are included more than once.
    seen_meas_types = set()
    dup_meas_types = set()
    for meas in measurements:
        if meas["measurement type"] in seen_meas_types:
            dup_meas_types.add(meas["measurement type"])
        else:
            seen_meas_types.add(meas["measurement type"])

    # Parse each object into readable information
    for meas in measurements:
        if meas["measurement type"] not in MEAS_TYPES:
            _LOGGER.debug(
                "UNKNOWN measurement type %s in BTHome BLE payload! Adv: %s",
                meas["measurement type"],
                payload.hex(),
            )
            continue

        if meas["measurement type"] in dup_meas_types:
            # Add a postfix for advertisements with multiple measurements of the same type
            postfix_counter = postfix_dict.get(meas["measurement type"], 0) + 1
            postfix_dict[meas["measurement type"]] = postfix_counter
            postfix = f"_{postfix_counter}"
        else:
            postfix = ""

        meas_type = MEAS_TYPES[meas["measurement type"]]
        meas_unit = meas_type.unit_of_measurement
        meas_format = meas_type.meas_format
        meas_factor = meas_type.factor
        value: None | str | int | float

        if meas["data format"] == 0 or meas["data format"] == "unsigned_integer":
            value = parse_uint(meas["measurement data"], meas_factor)
        elif meas["data format"] == 1 or meas["data format"] == "signed_integer":
            value = parse_int(meas["measurement data"], meas_factor)
        elif meas["data format"] == 2 or meas["data format"] == "float":
            value = parse_float(meas["measurement data"], meas_factor)
        elif meas["data format"] == 3 or meas["data format"] == "string":
            value = parse_string(meas["measurement data"])
        else:
            _LOGGER.error(
                "UNKNOWN dataobject in BTHome BLE payload! Adv: %s",
                payload.hex(),
            )
            continue

        if value is not None:
            result.update({meas_format: value})
            if meas_unit == "lbs":
                # Weight measurement with non-standard unit of measurement (lb)
                result.update({"weight unit": meas_unit})

    if not result:
        if self.report_unknown == "BTHome":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Home Assistant BLE DEVICE: RSSI: %s, MAC: %s, ADV: %s",
                self.rssi,
                to_mac(self.bthome_mac),
                payload.hex()
            )
        return None

    # Check for packet id in payload
    if result.get("packet"):
        self.packet_id = result["packet"]

    # Check for duplicate messages
    if self.packet_id:
        try:
            prev_packet = self.lpacket_ids[self.bthome_mac]
        except KeyError:
            # start with empty first packet
            prev_packet = None
        if prev_packet == self.packet_id:
            # only process new messages
            if self.filter_duplicates is True:
                return None
        self.lpacket_ids[self.bthome_mac] = self.packet_id
    else:
        self.packet_id = "no packet id"

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and self.bthome_mac not in self.sensor_whitelist:
        _LOGGER.debug("Discovery is disabled. MAC: %s is not whitelisted!", to_mac(self.bthome_mac))
        return None

    result.update({
        "rssi": self.rssi,
        "mac": to_unformatted_mac(self.bthome_mac),
        "packet": self.packet_id,
        "type": self.device_type,
        "firmware": self.firmware,
        "data": True
    })
    return result


def decrypt_data(self, data: bytes, sw_version: int):
    """Decrypt encrypted BTHome advertisements"""
    # check for minimum length of encrypted advertisement
    if len(data) < (15 if sw_version == 1 else 14):
        _LOGGER.debug("Invalid data length (for decryption), adv: %s", data.hex())
    # try to find encryption key for current device
    try:
        key = self.aeskeys[self.bthome_mac]
        if len(key) != 16:
            _LOGGER.error("Encryption key should be 16 bytes (32 characters) long")
            return None, None
    except KeyError:
        # no encryption key found
        _LOGGER.error("No encryption key found for device with MAC %s", to_mac(self.bthome_mac))
        return None, None

    # prepare the data for decryption
    if sw_version == 1:
        uuid = b"\x1e\x18"
    else:
        uuid = b"\xd2\xfc\x41"
    encrypted_payload = data[:-8]
    count_id = data[-8:-4]
    mic = data[-4:]

    # nonce: mac [6], uuid16 [2 (v1) or 3 (v2)], count_id [4]
    nonce = b"".join([self.bthome_mac, uuid, count_id])
    cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
    if sw_version == 1:
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
            to_mac(self.bthome_mac),
        )
        return None, None
    return decrypted_payload, count_id
