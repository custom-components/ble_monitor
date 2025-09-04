"""Parser for Sonoff BLE advertisements"""
import logging
from typing import Any

from .helpers import to_mac, to_unformatted_mac

_LOGGER = logging.getLogger(__name__)

SONOFF_MODEL_MAP = {
    0x46: "S-MATE",
    0x47: "R5"
}

SONOFF_BUTTON_MAP = {
    "S-MATE": {
        0x00: "three btn switch left",
        0x01: "three btn switch middle",
        0x02: "three btn switch right"
    },
    "R5": {
        0x00: "six btn switch top left",
        0x01: "six btn switch top middle",
        0x02: "six btn switch top right",
        0x03: "six btn switch bottom left",
        0x04: "six btn switch bottom middle",
        0x05: "six btn switch bottom right"
    }
}

SONOFF_ACTION_MAP = {
    0x00: "single press",
    0x01: "double press",
    0x02: "long press"
}


def decrypt_sonoff(encrypted_data: bytes, seed: int) -> bytes:
    xor_table = [0x0f, 0x39, 0xbe, 0x5f, 0x27, 0x05, 0xbe, 0xf9, 0x66, 0xb5,
                 0x74, 0x0d, 0x04, 0x86, 0xd2, 0x61, 0x55, 0xbb, 0xfc, 0x16,
                 0x34, 0x40, 0x7e, 0x1d, 0x38, 0x6e, 0xe4, 0x06, 0xaa, 0x79,
                 0x32, 0x95, 0x66, 0xb5, 0x74, 0x0d, 0xdb, 0x8c, 0xe9, 0x01,
                 0x2a]
    xor_table_len = len(xor_table)

    decrypted_data = bytearray()

    for i, b in enumerate(encrypted_data):
        decrypted_data.append(b ^ seed ^ xor_table[i % xor_table_len])

    return bytes(decrypted_data)


def parse_sonoff(self, data: bytes, mac: bytes) -> dict[str, Any] | None:
    # Verify MAC address and data length
    if mac != b"\x66\x55\x44\x33\x22\x11" or len(data) < 10:
        return None

    firmware = "Sonoff"

    # data_uuid32 = data[2:6]
    # data_magic_1 = data[6:10]
    data_device_type = data[10]
    # data_magic_2 = data[11]
    # data_sequence_number = data[12]
    data_device_id = data[13:17]
    data_seed = data[17]
    data_encrypted = data[18:]

    data_decrypted = decrypt_sonoff(data_encrypted, data_seed)

    # data_padding_1 = data_decrypted[0]
    data_button_id = data_decrypted[1]
    data_press_type = data_decrypted[2]
    data_press_counter = data_decrypted[3:7]
    # data_padding_2 = data_decrypted[7]
    # data_crc = data_decrypted[8:10]

    unique_mac = b"\x00\x00" + data_device_id

    # Check for duplicate messages
    packet_id = int.from_bytes(data_press_counter, "big")
    try:
        prev_packet = self.lpacket_ids[unique_mac]
    except KeyError:
        # start with empty first packet
        prev_packet = None
    if prev_packet == packet_id:
        # only process new messages
        if self.filter_duplicates is True:
            return None
    self.lpacket_ids[unique_mac] = packet_id

    try:
        device_type = SONOFF_MODEL_MAP[data_device_type]
    except KeyError:
        if self.report_unknown == "Sonoff":
            _LOGGER.info(
                "BLE ADV from UNKNOWN Sonoff DEVICE: MAC: %s, ADV: %s",
                to_mac(mac),
                data.hex()
            )
            return None

    try:
        result = {
            SONOFF_BUTTON_MAP[device_type][data_button_id]: "toggle",
            "button switch": SONOFF_ACTION_MAP[data_press_type]
        }
    except KeyError:
        _LOGGER.error(
            "Unknown button id (%s) or press type (%s) from Sonoff DEVICE: MAC: %s, ADV: %s",
            hex(data_button_id),
            hex(data_press_type),
            to_mac(mac),
            data.hex()
        )
        return None

    result.update({
        "mac": to_unformatted_mac(unique_mac),
        "type": device_type,
        "packet": packet_id,
        "firmware": firmware,
        "data": True
    })

    return result
