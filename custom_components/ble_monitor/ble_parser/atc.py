# Parser for ATC BLE advertisements
from Cryptodome.Cipher import AES
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)


def parse_atc(self, data, source_mac, rssi):
    # check for adstruc length
    device_type = "ATC"
    msg_length = len(data)
    if msg_length == 19:
        # Parse BLE message in Custom format without encryption
        firmware = "ATC (Custom)"
        atc_mac_reversed = data[4:10]
        atc_mac = atc_mac_reversed[::-1]
        (temp, humi, volt, batt, packet_id, trg) = unpack("<hHHBBB", data[10:])
        result = {
            "temperature": temp / 100,
            "humidity": humi / 100,
            "voltage": volt / 1000,
            "battery": batt,
            "switch": (trg >> 1) & 1,
            "opening": (trg ^ 1) & 1,
            "data": True
        }
        adv_priority = 39
    elif msg_length == 17:
        # Parse BLE message in ATC format
        firmware = "ATC (Atc1441)"
        atc_mac = data[4:10]
        (temp, humi, batt, volt, packet_id) = unpack(">hBBHB", data[10:])
        result = {
            "temperature": temp / 10,
            "humidity": humi,
            "voltage": volt / 1000,
            "battery": batt,
            "data": True
        }
        adv_priority = 29
    elif msg_length == 15:
        # Parse BLE message in Custom format with encryption
        atc_mac = source_mac
        packet_id = data[4]
        firmware = "ATC (Custom encrypted)"
        decrypted_data = decrypt_atc(self, data, atc_mac)
        if decrypted_data is None:
            result = {"data": False}
            adv_priority = 0
        else:
            (temp, humi, batt, trg) = unpack("<hHBB", decrypted_data)
            if batt > 100:
                batt = 100
            volt = 2.2 + (3.1 - 2.2) * (batt / 100)
            result = {
                "temperature": temp / 100,
                "humidity": humi / 100,
                "voltage": volt,
                "battery": batt,
                "switch": (trg >> 1) & 1,
                "opening": (trg ^ 1) & 1,
                "data": True
            }
            adv_priority = 39
    elif msg_length == 12:
        # Parse BLE message in Atc1441 format with encryption
        atc_mac = source_mac
        packet_id = data[4]
        firmware = "ATC (Atc1441 encrypted)"
        decrypted_data = decrypt_atc(self, data, atc_mac)
        if decrypted_data is None:
            result = {"data": False}
            adv_priority = 0
        else:
            temp = decrypted_data[0] / 2 - 40.0
            humi = decrypted_data[1] / 2
            batt = decrypted_data[2] & 0x7f
            trg = decrypted_data[2] >> 7
            if batt > 100:
                batt = 100
            volt = 2.2 + (3.1 - 2.2) * (batt / 100)
            result = {
                "temperature": temp,
                "humidity": humi,
                "voltage": volt,
                "battery": batt,
                "switch": trg,
                "data": True
            }
            adv_priority = 9
    else:
        if self.report_unknown == "ATC":
            _LOGGER.info(
                "BLE ADV from UNKNOWN ATC DEVICE: RSSI: %s, MAC: %s, AdStruct: %s",
                rssi,
                to_mac(source_mac),
                data.hex()
            )
        return None

    # check for MAC presence in sensor whitelist, if needed
    if self.discovery is False and atc_mac not in self.sensor_whitelist:
        return None

    try:
        prev_packet = self.lpacket_ids[atc_mac]
    except KeyError:
        # start with empty first packet
        prev_packet = None
    try:
        old_adv_priority = self.adv_priority[atc_mac]
    except KeyError:
        # start with initial adv priority
        old_adv_priority = 0
    if adv_priority > old_adv_priority:
        # always process advertisements with a higher priority
        self.adv_priority[atc_mac] = adv_priority
    elif adv_priority == old_adv_priority:
        if self.filter_duplicates is True:
            # only process messages with same priority that have a changed packet id
            if prev_packet == packet_id:
                return None
    else:
        # do not process advertisements with lower priority
        old_adv_priority -= 1
        self.adv_priority[atc_mac] = old_adv_priority
        return None
    self.lpacket_ids[atc_mac] = packet_id

    result.update({
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in atc_mac),
        "type": device_type,
        "packet": packet_id,
        "firmware": firmware
    })

    return result


def decrypt_atc(self, data, atc_mac):
    # try to find encryption key for current device
    try:
        key = self.aeskeys[atc_mac]
        if len(key) != 16:
            _LOGGER.error("Encryption key should be 16 bytes (32 characters) long")
    except KeyError:
        # no encryption key found
        _LOGGER.error("No encryption key found for ATC device with MAC: %s", to_mac(atc_mac))
        return None
    # prepare the data for decryption
    nonce = b"".join([atc_mac[::-1], data[:5]])
    cipherpayload = data[5:-4]
    aad = b"\x11"
    token = data[-4:]
    cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
    cipher.update(aad)
    # decrypt the data
    try:
        decrypted_payload = cipher.decrypt_and_verify(cipherpayload, token)
    except ValueError as error:
        _LOGGER.warning("Decryption failed: %s", error)
        _LOGGER.debug("token: %s", token.hex())
        _LOGGER.debug("nonce: %s", nonce.hex())
        _LOGGER.debug("encrypted_payload: %s", cipherpayload.hex())
        return None
    if decrypted_payload is None:
        _LOGGER.warning(
            "Decryption failed for %s, decrypted payload is None",
            to_mac(atc_mac),
        )
        return None

    return decrypted_payload


def to_mac(addr: int):
    return ':'.join('{:02x}'.format(x) for x in addr).upper()
