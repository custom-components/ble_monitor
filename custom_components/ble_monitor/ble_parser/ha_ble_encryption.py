"""Example showing encoding and decoding of HA BLE advertisement"""
import binascii
from Cryptodome.Cipher import AES


def parse_value(hexvalue):
    """Parse decrypted payload to readable HA BLE data"""
    vlength = len(hexvalue)
    if vlength >= 3:
        temp = round(int.from_bytes(hexvalue[2:4], "little", signed=False) * 0.01, 2)
        humi = round(int.from_bytes(hexvalue[6:8], "little", signed=False) * 0.01, 2)
        print("Temperature:", temp, "Humidity:", humi)
        return 1
    print("MsgLength:", vlength, "HexValue:", hexvalue.hex())
    return None


def decrypt_payload(payload, mic, key, nonce):
    """Decrypt payload."""
    print("Nonce:", nonce.hex())
    print("CryptData:", payload.hex(), "Mic:", mic.hex())
    cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
    cipher.update(b"\x11")
    try:
        data = cipher.decrypt_and_verify(payload, mic)
    except ValueError as error:
        print("Decryption failed:", error)
        return None
    print("DecryptData:", data.hex())
    print()
    if parse_value(data) is not None:
        return 1
    print('??')
    return None


def decrypt_aes_ccm(key, mac, data):
    """Decrypt AES CCM."""
    print("MAC:", mac.hex(), "Bindkey:", key.hex())
    print()
    adslength = len(data)
    if adslength > 15 and data[0] == 0x1E and data[1] == 0x18:
        pkt = data[:data[0] + 1]
        uuid = pkt[0:2]
        encrypted_data = pkt[2:-8]
        count_id = pkt[-8:-4]
        mic = pkt[-4:]
        # nonce: mac [6], uuid16 [2], count_id [4] # 6+2+4 = 12 bytes
        nonce = b"".join([mac, uuid, count_id])
        return decrypt_payload(encrypted_data, mic, key, nonce)
    else:
        print("Error: format packet!")
    return None


# =============================
# main()
# =============================
def main():
    """Encrypt payload."""
    print()
    print("====== Test encode -----------------------------------------")
    temp = 25.06
    humi = 50.55
    print("Temperature:", temp, "Humidity:", humi)
    print()
    data = bytes(bytearray.fromhex('2302CA090303BF13'))  # HA BLE data (not encrypted)
    count_id = bytes(bytearray.fromhex('00112233'))  # count id
    mac = binascii.unhexlify('5448E68F80A5')  # MAC
    uuid16 = b"\x1E\x18"
    bindkey = binascii.unhexlify('231d39c1d7cc1ab1aee224cd096db932')
    print("MAC:", mac.hex(), "Bindkey:", bindkey.hex())
    nonce = b"".join([mac, uuid16, count_id])  # 6+2+4 = 12 bytes
    cipher = AES.new(bindkey, AES.MODE_CCM, nonce=nonce, mac_len=4)
    cipher.update(b"\x11")
    ciphertext, mic = cipher.encrypt_and_digest(data)
    print("Data:", data.hex())
    print("Nonce:", nonce.hex())
    print("CryptData:", ciphertext.hex(), "Mic:", mic.hex())
    adstruct = b"".join([uuid16, ciphertext, count_id, mic])
    print()
    print("Encrypted data:", adstruct.hex())
    print()
    print("====== Test decode -----------------------------------------")
    decrypt_aes_ccm(bindkey, mac, adstruct)


if __name__ == '__main__':
    main()
