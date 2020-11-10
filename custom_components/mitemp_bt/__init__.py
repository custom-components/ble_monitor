"""Xiaomi passive BLE monitor sensor integration."""
import asyncio
from datetime import timedelta
import logging
import statistics as sts
import struct
from threading import Thread
from time import sleep
import voluptuous as vol

import aioblescan as aiobs
from Cryptodome.Cipher import AES

from homeassistant.const import (
    CONF_DEVICES,
    CONF_DISCOVERY,
    CONF_MAC,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import discovery

from .const import (
    DEFAULT_ROUNDING,
    DEFAULT_DECIMALS,
    DEFAULT_PERIOD,
    DEFAULT_LOG_SPIKES,
    DEFAULT_USE_MEDIAN,
    DEFAULT_ACTIVE_SCAN,
    DEFAULT_HCI_INTERFACE,
    DEFAULT_BATT_ENTITIES,
    DEFAULT_REPORT_UNKNOWN,
    DEFAULT_DISCOVERY,
    CONF_ROUNDING,
    CONF_DECIMALS,
    CONF_PERIOD,
    CONF_LOG_SPIKES,
    CONF_USE_MEDIAN,
    CONF_ACTIVE_SCAN,
    CONF_HCI_INTERFACE,
    CONF_BATT_ENTITIES,
    CONF_REPORT_UNKNOWN,
    CONF_TMIN,
    CONF_TMAX,
    CONF_HMIN,
    CONF_HMAX,
    CONF_ENCRYPTION_KEY,
    DOMAIN,
)

# regex constants for configuration schema
MAC_REGEX = "(?i)^(?:[0-9A-F]{2}[:]){5}(?:[0-9A-F]{2})$"
AES128KEY_REGEX = "(?i)^[A-F0-9]{32}$"

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_MAC): cv.string,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_ENCRYPTION_KEY): cv.matches_regex(AES128KEY_REGEX),
        vol.Optional(CONF_TEMPERATURE_UNIT): cv.temperature_unit,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_ROUNDING, default=DEFAULT_ROUNDING): cv.boolean,
                vol.Optional(CONF_DECIMALS, default=DEFAULT_DECIMALS): cv.positive_int,
                vol.Optional(CONF_PERIOD, default=DEFAULT_PERIOD): cv.positive_int,
                vol.Optional(CONF_LOG_SPIKES, default=DEFAULT_LOG_SPIKES): cv.boolean,
                vol.Optional(CONF_USE_MEDIAN, default=DEFAULT_USE_MEDIAN): cv.boolean,
                vol.Optional(CONF_ACTIVE_SCAN, default=DEFAULT_ACTIVE_SCAN): cv.boolean,
                vol.Optional(
                    CONF_HCI_INTERFACE, default=[DEFAULT_HCI_INTERFACE]
                ): vol.All(cv.ensure_list, [cv.positive_int]),
                vol.Optional(
                    CONF_BATT_ENTITIES, default=DEFAULT_BATT_ENTITIES
                ): cv.boolean,
                vol.Optional(
                    CONF_REPORT_UNKNOWN, default=DEFAULT_REPORT_UNKNOWN
                ): cv.boolean,
                vol.Optional(CONF_DISCOVERY, default=DEFAULT_DISCOVERY): cv.boolean,
                vol.Optional(CONF_DEVICES, default=[]): vol.All(
                    cv.ensure_list, [DEVICE_SCHEMA]
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
#def setup(hass, config):
    """Your controller/hub specific code."""
    conf = config[DOMAIN]
    active_scan = conf[CONF_ACTIVE_SCAN]
    hci_interfaces = conf[CONF_HCI_INTERFACE]

#    hass.data[DOMAIN] = {'temperature': 23}

    discovery.load_platform(hass, 'sensor', DOMAIN, {}, config)
    return True


# Structured objects for data conversions
TH_STRUCT = struct.Struct("<hH")
H_STRUCT = struct.Struct("<H")
T_STRUCT = struct.Struct("<h")
CND_STRUCT = struct.Struct("<H")
ILL_STRUCT = struct.Struct("<I")
FMDH_STRUCT = struct.Struct("<H")


class HCIdump(Thread):
    """Mimic deprecated hcidump tool."""

    def __init__(self, dumplist, interface=0, active=0):
        """Initiate HCIdump thread."""
        Thread.__init__(self)
        _LOGGER.debug("HCIdump thread: Init")
        self._interface = interface
        self._active = active
        self.dumplist = dumplist
        self._event_loop = None
        _LOGGER.debug("HCIdump thread: Init finished")

    def process_hci_events(self, data):
        """Collect HCI events."""
        self.dumplist.append(data)

    def run(self):
        """Run HCIdump thread."""
        _LOGGER.debug("HCIdump thread: Run")
        try:
            mysocket = aiobs.create_bt_socket(self._interface)
        except OSError as error:
            _LOGGER.error("HCIdump thread: OS error: %s", error)
        else:
            self._event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._event_loop)
            fac = self._event_loop._create_connection_transport(
                mysocket, aiobs.BLEScanRequester, None, None
            )
            _LOGGER.debug("HCIdump thread: Connection")
            conn, btctrl = self._event_loop.run_until_complete(fac)
            _LOGGER.debug("HCIdump thread: Connected")
            btctrl.process = self.process_hci_events
            btctrl.send_command(
                aiobs.HCI_Cmd_LE_Set_Scan_Params(scan_type=self._active)
            )
            btctrl.send_scan_request()
            _LOGGER.debug("HCIdump thread: start main event_loop")
            try:
                self._event_loop.run_forever()
            finally:
                _LOGGER.debug(
                    "HCIdump thread: main event_loop stopped, finishing",
                )
                btctrl.stop_scan_request()
                conn.close()
                self._event_loop.run_until_complete(asyncio.sleep(0))
                self._event_loop.close()
                _LOGGER.debug("HCIdump thread: Run finished")

    def join(self, timeout=10):
        """Join HCIdump thread."""
        _LOGGER.debug("HCIdump thread: joining")
        try:
            self._event_loop.call_soon_threadsafe(self._event_loop.stop)
        except AttributeError as error:
            _LOGGER.debug("%s", error)
        finally:
            Thread.join(self, timeout)
            _LOGGER.debug("HCIdump thread: joined")


def parse_xiaomi_value(hexvalue, typecode):
    """Convert value depending on its type."""
    vlength = len(hexvalue)
    if vlength == 4:
        if typecode == b'\x0D\x10':
            (temp, humi) = TH_STRUCT.unpack(hexvalue)
            return {"temperature": temp / 10, "humidity": humi / 10}
    if vlength == 2:
        if typecode == b'\x06\x10':
            (humi,) = H_STRUCT.unpack(hexvalue)
            return {"humidity": humi / 10}
        if typecode == b'\x04\x10':
            (temp,) = T_STRUCT.unpack(hexvalue)
            return {"temperature": temp / 10}
        if typecode == b'\x09\x10':
            (cond,) = CND_STRUCT.unpack(hexvalue)
            return {"conductivity": cond}
        if typecode == b'\x10\x10':
            (fmdh,) = FMDH_STRUCT.unpack(hexvalue)
            return {"formaldehyde": fmdh / 100}
    if vlength == 1:
        if typecode == b'\x0A\x10':
            return {"battery": hexvalue[0]}
        if typecode == b'\x08\x10':
            return {"moisture": hexvalue[0]}
        if typecode == b'\x12\x10':
            return {"switch": hexvalue[0]}
        if typecode == b'\x13\x10':
            return {"consumable": hexvalue[0]}
    if vlength == 3:
        if typecode == b'\x07\x10':
            (illum,) = ILL_STRUCT.unpack(hexvalue + b'\x00')
            return {"illuminance": illum}
    return None


def decrypt_payload(encrypted_payload, key, nonce):
    """Decrypt payload."""
    aad = b"\x11"
    token = encrypted_payload[-4:]
    payload_counter = encrypted_payload[-7:-4]
    nonce = b"".join([nonce, payload_counter])
    cipherpayload = encrypted_payload[:-7]
    cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
    cipher.update(aad)
    plaindata = None
    try:
        plaindata = cipher.decrypt_and_verify(cipherpayload, token)
    except ValueError as error:
        _LOGGER.error("Decryption failed: %s", error)
        _LOGGER.error("token: %s", token.hex())
        _LOGGER.error("nonce: %s", nonce.hex())
        _LOGGER.error("encrypted_payload: %s", encrypted_payload.hex())
        _LOGGER.error("cipherpayload: %s", cipherpayload.hex())
        return None
    return plaindata


def parse_raw_message(data, aeskeyslist,  whitelist, report_unknown=False):
    """Parse the raw data."""
    if data is None:
        return None
    # check for Xiaomi service data
    xiaomi_index = data.find(b'\x16\x95\xFE', 15)
    if xiaomi_index == -1:
        return None
    # check for no BR/EDR + LE General discoverable mode flags
    adv_index = data.find(b"\x02\x01\x06", 14, 17)
    adv_index2 = data.find(b"\x15\x16\x95", 14, 17)
    if adv_index == -1 and adv_index2 == -1:
        return None
    if adv_index2 != -1:
        adv_index = adv_index2
    # check for BTLE msg size
    msg_length = data[2] + 3
    if msg_length != len(data):
        return None
    # check for MAC presence in message and in service data
    xiaomi_mac_reversed = data[xiaomi_index + 8:xiaomi_index + 14]
    source_mac_reversed = data[adv_index - 7:adv_index - 1]
    if xiaomi_mac_reversed != source_mac_reversed:
        return None
    # check for MAC presence in whitelist, if needed
    if whitelist:
        if xiaomi_mac_reversed not in whitelist:
            return None
    # extract RSSI byte
    (rssi,) = struct.unpack("<b", data[msg_length - 1:msg_length])
    # strange positive RSSI workaround
    if rssi > 0:
        rssi = -rssi
    try:
        sensor_type = XIAOMI_TYPE_DICT[
            data[xiaomi_index + 5:xiaomi_index + 7]
        ]
    except KeyError:
        if report_unknown:
            _LOGGER.info(
                "BLE ADV from UNKNOWN: RSSI: %s, MAC: %s, ADV: %s",
                rssi,
                ''.join('{:02X}'.format(x) for x in xiaomi_mac_reversed[::-1]),
                data.hex()
            )
        return None
    # frame control bits
    framectrl, = struct.unpack('>H', data[xiaomi_index + 3:xiaomi_index + 5])
    # check data is present
    if not (framectrl & 0x4000):
        return None
    xdata_length = 0
    xdata_point = 0
    # check capability byte present
    if framectrl & 0x2000:
        xdata_length = -1
        xdata_point = 1
    # xiaomi data length = message length
    #     -all bytes before XiaomiUUID
    #     -3 bytes Xiaomi UUID + ADtype
    #     -1 byte rssi
    #     -3+1 bytes sensor type
    #     -1 byte packet_id
    #     -6 bytes MAC
    #     - capability byte offset
    xdata_length += msg_length - xiaomi_index - 15
    if xdata_length < 3:
        return None
    xdata_point += xiaomi_index + 14
    # check if xiaomi data start and length is valid
    if xdata_length != len(data[xdata_point:-1]):
        return None
    # check encrypted data flags
    if framectrl & 0x0800:
        # try to find encryption key for current device
        try:
            key = aeskeyslist[xiaomi_mac_reversed]
        except KeyError:
            # no encryption key found
            return None
        nonce = b"".join(
            [
                xiaomi_mac_reversed,
                data[xiaomi_index + 5:xiaomi_index + 7],
                data[xiaomi_index + 7:xiaomi_index + 8]
            ]
        )
        decrypted_payload = decrypt_payload(
            data[xdata_point:msg_length-1], key, nonce
        )
        if decrypted_payload is None:
            _LOGGER.error(
                "Decryption failed for %s, decrypted payload is None",
                "".join("{:02X}".format(x) for x in xiaomi_mac_reversed[::-1]),
            )
            return None
        # replace cipher with decrypted data
        msg_length -= len(data[xdata_point:msg_length-1])
        data = b"".join((data[:xdata_point], decrypted_payload, data[-1:]))
        msg_length += len(decrypted_payload)
    packet_id = data[xiaomi_index + 7]
    result = {
        "rssi": rssi,
        "mac": ''.join('{:02X}'.format(x) for x in xiaomi_mac_reversed[::-1]),
        "type": sensor_type,
        "packet": packet_id,
    }
    # loop through xiaomi payload
    # assume that the data may have several values of different types,
    # although I did not notice this behavior with my LYWSDCGQ sensors
    while True:
        xvalue_typecode = data[xdata_point:xdata_point + 2]
        try:
            xvalue_length = data[xdata_point + 2]
        except ValueError as error:
            _LOGGER.error("xvalue_length conv. error: %s", error)
            _LOGGER.error("xdata_point: %s", xdata_point)
            _LOGGER.error("data: %s", data.hex())
            result = {}
            break
        except IndexError as error:
            _LOGGER.error("Wrong xdata_point: %s", error)
            _LOGGER.error("xdata_point: %s", xdata_point)
            _LOGGER.error("data: %s", data.hex())
            result = {}
            break
        xnext_point = xdata_point + 3 + xvalue_length
        xvalue = data[xdata_point + 3:xnext_point]
        res = parse_xiaomi_value(xvalue, xvalue_typecode)
        if res:
            result.update(res)
        if xnext_point > msg_length - 3:
            break
        xdata_point = xnext_point
    return result


def temperature_limit(config, mac, temp):
    """Set limits for temperature measurement in °C or °F."""
    fmac = ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))

    if config[DOMAIN][CONF_DEVICES]:
        for device in config[DOMAIN][CONF_DEVICES]:
            if fmac in device["mac"].upper():
                if "temperature_unit" in device:
                    if device["temperature_unit"] == TEMP_FAHRENHEIT:
                        temp_fahrenheit = temp * 9 / 5 + 32
                        return temp_fahrenheit
                break
    return temp


class BLEScanner:
    """BLE scanner."""
    dumpthreads = []
    hcidump_data = []

    def start(self, active_scan, hci_interfaces):
        """Start receiving broadcasts."""
        _LOGGER.debug("active scan is %s", active_scan)
        self.hcidump_data.clear()
        _LOGGER.debug("Spawning HCIdump thread(s).")
        for hci_int in hci_interfaces:
            dumpthread = HCIdump(
                dumplist=self.hcidump_data,
                interface=hci_int,
                active=int(active_scan is True),
            )
            self.dumpthreads.append(dumpthread)
            _LOGGER.debug("Starting HCIdump thread for hci%s", hci_int)
            dumpthread.start()
        _LOGGER.debug("HCIdump threads count = %s", len(self.dumpthreads))

    def stop(self):
        """Stop HCIdump thread(s)."""
        result = True
        for dumpthread in self.dumpthreads:
            if dumpthread.is_alive():
                dumpthread.join()
                if dumpthread.is_alive():
                    result = False
                    _LOGGER.error(
                        "Waiting for the HCIdump thread to finish took too long! (>10s)"
                    )
        if result is True:
            self.dumpthreads.clear()
        return result

    def shutdown_handler(self, event):
        """Run homeassistant_stop event handler."""
        _LOGGER.debug("Running homeassistant_stop event handler: %s", event)
        self.stop()
