#!/usr/bin/env python3
"""Anonymize Xiaomi MiBeacon V4/V5 encrypted raw advertisements."""

from __future__ import annotations

import argparse
from dataclasses import dataclass

from Cryptodome.Cipher import AES


@dataclass
class AdStructure:
    start: int
    size: int
    value: bytes


def _parse_ad_structures(raw: bytes) -> tuple[list[AdStructure], int, int, bool]:
    if len(raw) < 4:
        raise ValueError("Raw BLE HCI event is too short to determine advertisement packet type")
    is_ext_packet = raw[3] == 0x0D
    adpayload_start = 29 if is_ext_packet else 14
    if len(raw) < adpayload_start:
        packet_type = "extended" if is_ext_packet else "legacy"
        raise ValueError(f"Raw {packet_type} BLE HCI event is too short; expected at least {adpayload_start} bytes")
    adpayload_size = raw[adpayload_start - 1]
    if len(raw) < adpayload_start + adpayload_size:
        raise ValueError(
            f"Raw BLE HCI event is shorter than the advertised payload length ({adpayload_size} bytes)"
        )
    structures: list[AdStructure] = []
    cursor = adpayload_start
    remaining = adpayload_size
    while remaining > 1:
        adstruct_size = raw[cursor] + 1
        if adstruct_size <= 1 or adstruct_size > remaining:
            break
        chunk = raw[cursor:cursor + adstruct_size]
        structures.append(AdStructure(cursor, adstruct_size, chunk))
        cursor += adstruct_size
        remaining -= adstruct_size
    return structures, adpayload_start, adpayload_size, is_ext_packet


def _extract_mac(raw: bytes, is_ext_packet: bool) -> bytes:
    min_length = 14 if is_ext_packet else 13
    if len(raw) < min_length:
        packet_type = "extended" if is_ext_packet else "legacy"
        raise ValueError(f"Raw {packet_type} BLE HCI event is too short to contain a MAC address")
    return (raw[8:14] if is_ext_packet else raw[7:13])[::-1]


def _calc_payload_start(service_data: bytes, mac: bytes) -> int:
    if len(service_data) < 9:
        raise ValueError("Xiaomi FE95 service data is too short; expected at least 9 bytes")
    i = 9
    frame_control = service_data[4] + (service_data[5] << 8)
    mac_include = (frame_control >> 4) & 1
    capability_include = (frame_control >> 5) & 1
    if mac_include:
        i += 6
        if len(service_data) < i:
            raise ValueError("Xiaomi FE95 service data is too short to contain the embedded MAC address")
        embedded_mac = service_data[9:15][::-1]
        if embedded_mac != mac:
            raise ValueError("MAC in Xiaomi payload does not match advertisement MAC")
    if capability_include:
        i += 1
        if len(service_data) < i:
            raise ValueError("Xiaomi FE95 service data is too short to contain the capability byte")
        capability_types = service_data[i - 1]
        if capability_types & 0x20:
            i += 1
            if len(service_data) < i:
                raise ValueError("Xiaomi FE95 service data is too short to contain the capability IO byte")
    return i


def _decrypt_payload(service_data: bytes, mac: bytes, key: bytes) -> tuple[bytes, int]:
    payload_start = _calc_payload_start(service_data, mac)
    if len(service_data) < payload_start + 7:
        raise ValueError("Xiaomi FE95 service data is too short to contain an encrypted payload and authentication tag")
    nonce = b"".join([mac[::-1], service_data[6:9], service_data[-7:-4]])
    cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
    cipher.update(b"\x11")
    plaintext = cipher.decrypt_and_verify(service_data[payload_start:-7], service_data[-4:])
    return plaintext, payload_start


def _encrypt_payload(service_data: bytearray, new_mac: bytes, new_key: bytes, payload_start: int, plaintext: bytes) -> bytes:
    frame_control = service_data[4] + (service_data[5] << 8)
    mac_include = (frame_control >> 4) & 1
    if mac_include:
        service_data[9:15] = new_mac[::-1]
    nonce = b"".join([new_mac[::-1], bytes(service_data[6:9]), bytes(service_data[-7:-4])])
    cipher = AES.new(new_key, AES.MODE_CCM, nonce=nonce, mac_len=4)
    cipher.update(b"\x11")
    encrypted = cipher.encrypt(plaintext)
    token = cipher.digest()
    rebuilt = bytearray(service_data)
    rebuilt[payload_start:-7] = encrypted
    rebuilt[-4:] = token
    return bytes(rebuilt)


def anonymize_xiaomi_mibeacon_v5(raw_hex: str, real_key_hex: str, new_mac_hex: str, new_key_hex: str) -> dict[str, str]:
    raw = bytearray.fromhex(raw_hex)
    real_key = bytes.fromhex(real_key_hex)
    new_key = bytes.fromhex(new_key_hex)
    new_mac = bytes.fromhex(new_mac_hex)
    structures, _, _, is_ext_packet = _parse_ad_structures(raw)
    old_mac = _extract_mac(raw, is_ext_packet)
    service_ad = next(
        (
            item
            for item in structures
            if item.size > 4 and item.value[1] == 0x16 and item.value[2] == 0x95 and item.value[3] == 0xFE
        ),
        None,
    )
    if service_ad is None:
        raise ValueError("No Xiaomi FE95 service data found in raw advertisement")
    service_data = service_ad.value
    plaintext, payload_start = _decrypt_payload(service_data, old_mac, real_key)
    encrypted_service_data = _encrypt_payload(bytearray(service_data), new_mac, new_key, payload_start, plaintext)
    raw[service_ad.start:service_ad.start + service_ad.size] = encrypted_service_data
    if is_ext_packet:
        raw[8:14] = new_mac[::-1]
    else:
        raw[7:13] = new_mac[::-1]
    verify_plaintext, _ = _decrypt_payload(bytes(encrypted_service_data), new_mac, new_key)
    if verify_plaintext != plaintext:
        raise ValueError("Verification failed: payload mismatch after re-encryption")
    return {
        "old_mac": old_mac.hex().upper(),
        "new_mac": new_mac.hex().upper(),
        "new_key": new_key.hex(),
        "raw": bytes(raw).hex().upper(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Anonymize Xiaomi MiBeacon V4/V5 encrypted advertisements")
    parser.add_argument("--raw", required=True, help="Raw BLE HCI event hex string")
    parser.add_argument("--key", required=True, help="Original 16-byte AES key hex")
    parser.add_argument("--new-mac", default="112233445566", help="Anonymized MAC hex, default: 112233445566")
    parser.add_argument(
        "--new-key",
        default="00112233445566778899aabbccddeeff",
        help="Anonymized 16-byte AES key hex, default: 00112233445566778899aabbccddeeff",
    )
    args = parser.parse_args()
    result = anonymize_xiaomi_mibeacon_v5(args.raw, args.key, args.new_mac, args.new_key)
    print(f"old_mac={result['old_mac']}")
    print(f"new_mac={result['new_mac']}")
    print(f"new_key={result['new_key']}")
    print(f"raw={result['raw']}")


if __name__ == "__main__":
    main()
