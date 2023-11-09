#!/usr/bin/env python3

# Usage:
#   pip3 install bleak asyncio
#   python3 get_beacon_key.py <MAC> <PRODUCT_ID>
#
# List of PRODUCT_ID:
#   339: For 'YLYK01YL'
#   950: For 'YLKG07YL/YLKG08YL'
#   959: For 'YLYB01YL-BHFRC'
#   1254: For 'YLYK01YL-VENFAN'
#   1678: For 'YLYK01YL-FANCL'
#
# Example:
#   python3 get_beacon_key.py AB:CD:EF:12:34:56 950

import asyncio
import random
import re
import sys

from bleak import BleakClient
from bleak.uuids import normalize_uuid_16

MAC_PATTERN = r"^[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}$"

UUID_SERVICE = "fe95"

# The characteristics of the 'fe95' service have unique uuid values and thus can be addressed via their uuid
# this can be checked by using the service explorer from https://github.com/hbldh/bleak/blob/master/examples/service_explorer.py
HANDLE_AUTH = normalize_uuid_16(0x0001)
HANDLE_FIRMWARE_VERSION = normalize_uuid_16(0x0004)
HANDLE_AUTH_INIT = normalize_uuid_16(0x0010)
HANDLE_BEACON_KEY = normalize_uuid_16(0x0014)

MI_KEY1 = bytes([0x90, 0xCA, 0x85, 0xDE])
MI_KEY2 = bytes([0x92, 0xAB, 0x54, 0xFA])
SUBSCRIBE_TRUE = bytes([0x01, 0x00])


def reverseMac(mac) -> bytes:
    parts = mac.split(":")
    reversedMac = bytearray()
    leng = len(parts)
    for i in range(1, leng + 1):
        reversedMac.extend(bytearray.fromhex(parts[leng - i]))
    return reversedMac


def mixA(mac, productID) -> bytes:
    return bytes([mac[0], mac[2], mac[5], (productID & 0xff), (productID & 0xff), mac[4], mac[5], mac[1]])


def mixB(mac, productID) -> bytes:
    return bytes([mac[0], mac[2], mac[5], ((productID >> 8) & 0xff), mac[4], mac[0], mac[5], (productID & 0xff)])


def cipherInit(key) -> bytes:
    perm = bytearray()
    for i in range(0, 256):
        perm.extend(bytes([i & 0xff]))
    keyLen = len(key)
    j = 0
    for i in range(0, 256):
        j += perm[i] + key[i % keyLen]
        j = j & 0xff
        perm[i], perm[j] = perm[j], perm[i]
    return perm


def cipherCrypt(input, perm) -> bytes:
    index1 = 0
    index2 = 0
    output = bytearray()
    for i in range(0, len(input)):
        index1 = index1 + 1
        index1 = index1 & 0xff
        index2 += perm[index1]
        index2 = index2 & 0xff
        perm[index1], perm[index2] = perm[index2], perm[index1]
        idx = perm[index1] + perm[index2]
        idx = idx & 0xff
        outputByte = input[i] ^ perm[idx]
        output.extend(bytes([outputByte & 0xff]))
    return output


def cipher(key, input) -> bytes:
    # More information: https://github.com/drndos/mikettle
    perm = cipherInit(key)
    return cipherCrypt(input, perm)


def generateRandomToken() -> bytes:
    token = bytearray()
    for i in range(0, 12):
        token.extend(bytes([random.randint(0, 255)]))
    return token


async def get_beacon_key(mac, product_id):
    reversed_mac = reverseMac(mac)
    token = generateRandomToken()

    # Pairing
    input(f"Activate pairing on your '{mac}' device, then press Enter: ")

    # Connect
    print("Connection in progress...")
    client = BleakClient(mac)
    try:
        await client.connect()
        print("Successful connection!")

        # An asyncio future object is needed for callback handling
        future = asyncio.get_event_loop().create_future()

        # Auth (More information: https://github.com/archaron/docs/blob/master/BLE/ylkg08y.md)
        print("Authentication in progress...")

        # Send 0x90, 0xCA, 0x85, 0xDE bytes to authInitCharacteristic.
        await client.write_gatt_char(HANDLE_AUTH_INIT, MI_KEY1, True)
        # Subscribe authCharacteristic.
        # (a lambda callback is used to set the futures result on the notification event)
        await client.start_notify(HANDLE_AUTH, lambda _, data: future.set_result(data))
        # Send cipher(mixA(reversedMac, productID), token) to authCharacteristic.
        await client.write_gatt_char(HANDLE_AUTH, cipher(mixA(reversed_mac, product_id), token), True)
        # Now you'll get a notification on authCharacteristic. You must wait for this notification before proceeding to next step
        await asyncio.wait_for(future, 10.0)

        # The notification data can be ignored or used to check an integrity, this is optional
        print(f"notifyData:  '{future.result().hex()}'")
        # If you want to perform a check, compare cipher(mixB(reversedMac, productID), cipher(mixA(reversedMac, productID), res))
        # where res is received payload ...
        print(f"cipheredRes: '{cipher(mixB(reversed_mac, product_id), cipher(mixA(reversed_mac, product_id), future.result())).hex()}'")
        # ... with your token, they must equal.
        print(f"randomToken: '{token.hex()}'")

        # Send 0x92, 0xAB, 0x54, 0xFA to authCharacteristic.
        await client.write_gatt_char(HANDLE_AUTH, cipher(token, MI_KEY2), True)
        print("Successful authentication!")

        # Read
        beacon_key = cipher(token, await client.read_gatt_char(HANDLE_BEACON_KEY)).hex()
        # Read from verCharacteristics. You can ignore the response data, you just have to perform a read to complete authentication process.
        # If the data is used, it will show the firmware version
        firmware_version = cipher(token, await client.read_gatt_char(HANDLE_FIRMWARE_VERSION)).decode()

        print(f"beaconKey: '{beacon_key}'")
        print(f"firmware_version: '{firmware_version}'")

        print("Disconnection in progress...")
    except Exception as e:
        print(e)
    finally:
        await client.disconnect()
        print("Disconnected!")


async def main(argv):
    # ARGS
    if len(argv) <= 2:
        print("usage: get_beacon_key.py <MAC> <PRODUCT_ID>\n")
        print("PRODUCT_ID:")
        print("  339: For 'YLYK01YL'")
        print("  950: For 'YLKG07YL/YLKG08YL'")
        print("  959: For 'YLYB01YL-BHFRC'")
        print("  1254: For 'YLYK01YL-VENFAN'")
        print("  1678: For 'YLYK01YL-FANCL'")
        return

    # MAC
    mac = argv[1].upper()
    if not re.compile(MAC_PATTERN).match(mac):
        print(f"[ERROR] The MAC address '{mac}' seems to be in the wrong format")
        return

    # PRODUCT_ID
    product_id = argv[2]
    try:
        product_id = int(product_id)
    except Exception:
        print(f"[ERROR] The Product Id '{product_id}' seems to be in the wrong format")
        return

    # BEACON_KEY
    await get_beacon_key(mac, product_id)


if __name__ == '__main__':
    asyncio.run(main(sys.argv))
