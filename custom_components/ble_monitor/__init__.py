"""Passive BLE monitor integration."""
import asyncio
import logging
import queue
import struct
from threading import Thread
import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    CONF_DEVICES,
    CONF_DISCOVERY,
    CONF_MAC,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import discovery

from Cryptodome.Cipher import AES

# It was decided to temporarily include this file in the integration bundle
# until the issue with checking the adapter's capabilities is resolved in the official aioblescan repo
# see https://github.com/frawau/aioblescan/pull/30, thanks to @vicamo
from . import aioblescan_ext as aiobs

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
    DEFAULT_RESTORE_STATE,
    CONF_ROUNDING,
    CONF_DECIMALS,
    CONF_PERIOD,
    CONF_LOG_SPIKES,
    CONF_USE_MEDIAN,
    CONF_ACTIVE_SCAN,
    CONF_HCI_INTERFACE,
    CONF_BATT_ENTITIES,
    CONF_REPORT_UNKNOWN,
    CONF_RESTORE_STATE,
    CONF_ENCRYPTION_KEY,
    DOMAIN,
    XIAOMI_TYPE_DICT,
    MAC_REGEX,
    AES128KEY_REGEX,
)

_LOGGER = logging.getLogger(__name__)

# Structured objects for data conversions
TH_STRUCT = struct.Struct("<hH")
H_STRUCT = struct.Struct("<H")
T_STRUCT = struct.Struct("<h")
CND_STRUCT = struct.Struct("<H")
ILL_STRUCT = struct.Struct("<I")
FMDH_STRUCT = struct.Struct("<H")

PLATFORMS = ["binary_sensor", "sensor"]

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_MAC): cv.matches_regex(MAC_REGEX),
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_ENCRYPTION_KEY): cv.matches_regex(AES128KEY_REGEX),
        vol.Optional(CONF_TEMPERATURE_UNIT): cv.temperature_unit,
    }
)


async def async_setup(hass, config):
    """Set up integration."""

    if not DOMAIN in config:
        return True
    
    _LOGGER.info("Initializing BLE Monitor integration")
    hass.async_add_job(hass.config_entries.flow.async_init(
    DOMAIN, context={"source": SOURCE_IMPORT}, data=config[DOMAIN]
    ))

    # NOT SURE ABOUT THIS PART. PROBABLY ALSO IN ASYNC_SETUP_ENTRY. TEST TOMORROW
    blemonitor = BLEmonitor(config[DOMAIN])
    hass.bus.async_listen(EVENT_HOMEASSISTANT_STOP, blemonitor.shutdown_handler)
    blemonitor.start()
    hass.data[DOMAIN] = blemonitor # NOT SURE HOW TO CONVERT THIS ONE
    # discovery.load_platform(hass, "sensor", DOMAIN, {}, config) # REMOVE? WILL BE LOADED IN hass.config_entries.async_forward_entry_setup
    # discovery.load_platform(hass, "binary_sensor", DOMAIN, {}, config) # REMOVE? WILL BE LOADED IN hass.config_entries.async_forward_entry_setup
    # END NOT SURE ABOUT THIS PART. TEST TOMORROW

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up BLE Monitor from a config entry."""
    _LOGGER.info("Initializing BLE Monitor entry")

    if not entry.unique_id:
        hass.config_entries.async_update_entry(entry, unique_id=entry.title)

    if not entry.options:
        # Move settings to options after initial setup
        options = entry.data
        data = {}
        hass.config_entries.async_update_entry(entry, data=data, options=options)

    entry.add_update_listener(_async_update_listener)

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )

    return unload_ok

async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
    

class BLEmonitor:
    """BLE scanner."""

    def __init__(self, config):
        """Init."""
        self.dataqueue = {
            "binary": queue.Queue(),
            "measuring": queue.Queue(),
        }
        self.config = config
        self.dumpthread = None

    def shutdown_handler(self, event):
        """Run homeassistant_stop event handler."""
        _LOGGER.debug("Shutdown event fired: %s", event)
        self.stop()

    def start(self):
        """Start receiving broadcasts."""
        _LOGGER.debug("Spawning HCIdump thread")
        self.dumpthread = HCIdump(
            config=self.config,
            dataqueue=self.dataqueue,
        )
        self.dumpthread.start()

    def stop(self):
        """Stop HCIdump thread(s)."""
        self.dataqueue["binary"].put(None)
        self.dataqueue["measuring"].put(None)
        result = True
        if self.dumpthread is None:
            _LOGGER.debug("BLE monitor stopped")
            return True
        if self.dumpthread.is_alive():
            self.dumpthread.join()
            if self.dumpthread.is_alive():
                result = False
                _LOGGER.error(
                    "Waiting for the HCIdump thread to finish took too long! (>10s)"
                )
        _LOGGER.debug("BLE monitor stopped")
        return result

    def restart(self):
        """Restart scanning"""
        if self.dumpthread.is_alive():
            self.dumpthread.restart()
        else:
            self.start()


class HCIdump(Thread):
    """Mimic deprecated hcidump tool."""

    def __init__(self, config, dataqueue):
        """Initiate HCIdump thread."""

        def obj0d10(xobj):
            (temp, humi) = TH_STRUCT.unpack(xobj)
            return {"temperature": temp / 10, "humidity": humi / 10}

        def obj0610(xobj):
            (humi,) = H_STRUCT.unpack(xobj)
            return {"humidity": humi / 10}

        def obj0410(xobj):
            (temp,) = T_STRUCT.unpack(xobj)
            return {"temperature": temp / 10}

        def obj0910(xobj):
            (cond,) = CND_STRUCT.unpack(xobj)
            return {"conductivity": cond}

        def obj1010(xobj):
            (fmdh,) = FMDH_STRUCT.unpack(xobj)
            return {"formaldehyde": fmdh / 100}

        def obj0a10(xobj):
            return {"battery": xobj[0]}

        def obj0810(xobj):
            return {"moisture": xobj[0]}

        def obj1210(xobj):
            return {"switch": xobj[0]}

        def obj1810(xobj):
            return {"light": xobj[0]}

        def obj1910(xobj):
            return {"opening": xobj[0]}

        def obj1310(xobj):
            return {"consumable": xobj[0]}

        def obj0710(xobj):
            (illum,) = ILL_STRUCT.unpack(xobj + b'\x00')
            return {"illuminance": illum}

        def obj0510(xobj):
            return {"switch": xobj[0], "temperature": xobj[1]}

        def reverse_mac(rmac):
            """Change LE order to BE."""
            if len(rmac) != 12:
                return None
            return rmac[10:12] + rmac[8:10] + rmac[6:8] + rmac[4:6] + rmac[2:4] + rmac[0:2]

        Thread.__init__(self)
        _LOGGER.debug("HCIdump thread: Init")
        self.dataqueue_bin = dataqueue["binary"]
        self.dataqueue_meas = dataqueue["measuring"]
        self._event_loop = None
        self._joining = False
        self.evt_cnt = 0
        self.lpacket_ids = {}
        self.config = config
        self._interfaces = config[CONF_HCI_INTERFACE]
        self._active = int(config[CONF_ACTIVE_SCAN] is True)
        self.discovery = True
        self.aeskeys = {}
        self.whitelist = []
        self.report_unknown = False
        if self.config[CONF_REPORT_UNKNOWN]:
            self.report_unknown = True
            _LOGGER.info(
                "Attention! Option report_unknown is enabled, be ready for a huge output..."
            )
        # prepare device:key lists to speedup parser
        if self.config[CONF_DEVICES]:
            for device in self.config[CONF_DEVICES]:
                if "encryption_key" in device:
                    p_mac = bytes.fromhex(
                        reverse_mac(device["mac"].replace(":", "")).lower()
                    )
                    p_key = bytes.fromhex(device["encryption_key"].lower())
                    self.aeskeys[p_mac] = p_key
                else:
                    continue
        _LOGGER.debug("%s encryptors mac:key pairs loaded.", len(self.aeskeys))
        if isinstance(self.config[CONF_DISCOVERY], bool):
            if self.config[CONF_DISCOVERY] is False:
                self.discovery = False
                if self.config[CONF_DEVICES]:
                    for device in self.config[CONF_DEVICES]:
                        self.whitelist.append(device["mac"])
        # remove duplicates from whitelist
        self.whitelist = list(dict.fromkeys(self.whitelist))
        _LOGGER.debug("whitelist: [%s]", ", ".join(self.whitelist).upper())
        for i, mac in enumerate(self.whitelist):
            self.whitelist[i] = bytes.fromhex(reverse_mac(mac.replace(":", "")).lower())
        _LOGGER.debug("%s whitelist item(s) loaded.", len(self.whitelist))
        # dataobject dictionary to implement switch-case statement
        # dataObject id  (converter, binary, measuring)
        self._dataobject_dict = {
            b'\x0D\x10': (obj0d10, False, True),
            b'\x06\x10': (obj0610, False, True),
            b'\x04\x10': (obj0410, False, True),
            b'\x09\x10': (obj0910, False, True),
            b'\x10\x10': (obj1010, False, True),
            b'\x0A\x10': (obj0a10, True, True),
            b'\x08\x10': (obj0810, False, True),
            b'\x12\x10': (obj1210, True, False),
            b'\x18\x10': (obj1810, True, False),
            b'\x19\x10': (obj1910, True, False),
            b'\x13\x10': (obj1310, False, True),
            b'\x07\x10': (obj0710, False, True),
            b'\x05\x10': (obj0510, True, True),
        }

    def process_hci_events(self, data):
        """Parses HCI events."""
        self.evt_cnt += 1
        msg, binary, measuring = self.parse_raw_message(data)
        if msg:
            if binary == measuring:
                self.dataqueue_bin.put(msg)
                self.dataqueue_meas.put(msg)
            else:
                if binary is True:
                    self.dataqueue_bin.put(msg)
                if measuring is True:
                    self.dataqueue_meas.put(msg)

    def run(self):
        """Run HCIdump thread."""
        while True:
            _LOGGER.debug("HCIdump thread: Run")
            mysocket = {}
            fac = {}
            conn = {}
            btctrl = {}
            if self._event_loop is None:
                self._event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._event_loop)
            for hci in self._interfaces:
                try:
                    mysocket[hci] = aiobs.create_bt_socket(hci)
                except OSError as error:
                    _LOGGER.error("HCIdump thread: OS error (hci%i): %s", hci, error)
                else:
                    fac[hci] = getattr(self._event_loop, "_create_connection_transport")(
                        mysocket[hci], aiobs.BLEScanRequester, None, None
                    )
                    conn[hci], btctrl[hci] = self._event_loop.run_until_complete(fac[hci])
                    _LOGGER.debug("HCIdump thread: connected to hci%i", hci)
                    btctrl[hci].process = self.process_hci_events
                    self._event_loop.run_until_complete(btctrl[hci].send_scan_request(self._active))
            _LOGGER.debug("HCIdump thread: start main event_loop")
            try:
                self._event_loop.run_forever()
            finally:
                _LOGGER.debug("HCIdump thread: main event_loop stopped, finishing")
                for hci in self._interfaces:
                    try:
                        self._event_loop.run_until_complete(btctrl[hci].stop_scan_request())
                        conn[hci].close()
                    except KeyError as error:
                        _LOGGER.error("HCIdump thread finishing: Key Error, no device on hci%i", hci)
                self._event_loop.run_until_complete(asyncio.sleep(0))
            if self._joining is True:
                break
            _LOGGER.debug("HCIdump thread: Scanning will be restarted")
            _LOGGER.debug("%i HCI events processed for previous period.", self.evt_cnt)
            self.evt_cnt = 0
        self._event_loop.close()
        _LOGGER.debug("HCIdump thread: Run finished")

    def join(self, timeout=10):
        """Join HCIdump thread."""
        _LOGGER.debug("HCIdump thread: joining")
        self._joining = True
        try:
            self._event_loop.call_soon_threadsafe(self._event_loop.stop)
        except AttributeError as error:
            _LOGGER.debug("%s", error)
        finally:
            Thread.join(self, timeout)
            _LOGGER.debug("HCIdump thread: joined")

    def restart(self):
        """Restarting scanner"""
        try:
            self._event_loop.call_soon_threadsafe(self._event_loop.stop)
        except AttributeError as error:
            _LOGGER.debug("%s", error)

    def parse_raw_message(self, data):
        """Parse the raw data."""
        # check if packet is Extended scan result
        is_ext_packet = True if data[3] == 0x0d else False
        # check for Xiaomi service data
        xiaomi_index = data.find(b'\x16\x95\xFE', 15 + 15 if is_ext_packet else 0)
        if xiaomi_index == -1:
            return None, None, None
        # check for no BR/EDR + LE General discoverable mode flags
        advert_start = 29 if is_ext_packet else 14
        adv_index = data.find(b"\x02\x01\x06", advert_start, 3 + advert_start)
        adv_index2 = data.find(b"\x15\x16\x95", advert_start, 3 + advert_start)
        if adv_index == -1 and adv_index2 == -1:
            return None, None, None
        if adv_index2 != -1:
            adv_index = adv_index2
        # check for BTLE msg size
        msg_length = data[2] + 3
        if msg_length != len(data):
            return None, None, None
        # check for MAC presence in message and in service data
        xiaomi_mac_reversed = data[xiaomi_index + 8:xiaomi_index + 14]
        mac_index = adv_index - 14 if is_ext_packet else adv_index
        source_mac_reversed = data[mac_index - 7:mac_index - 1]
        if xiaomi_mac_reversed != source_mac_reversed:
            return None, None, None
        # check for MAC presence in whitelist, if needed
        if self.discovery is False:
            if xiaomi_mac_reversed not in self.whitelist:
                return None, None, None
        packet_id = data[xiaomi_index + 7]
        try:
            prev_packet = self.lpacket_ids[xiaomi_mac_reversed]
        except KeyError:
            prev_packet = None, None, None
        if prev_packet == packet_id:
            return None, None, None
        self.lpacket_ids[xiaomi_mac_reversed] = packet_id
        # extract RSSI byte
        rssi_index = 18 if is_ext_packet else msg_length - 1
        (rssi,) = struct.unpack("<b", data[rssi_index:rssi_index + 1])
        # strange positive RSSI workaround
        if rssi > 0:
            rssi = -rssi
        try:
            sensor_type, binary_data = XIAOMI_TYPE_DICT[
                data[xiaomi_index + 5:xiaomi_index + 7]
            ]
        except KeyError:
            if self.report_unknown:
                _LOGGER.info(
                    "BLE ADV from UNKNOWN: RSSI: %s, MAC: %s, ADV: %s",
                    rssi,
                    ''.join('{:02X}'.format(x) for x in xiaomi_mac_reversed[::-1]),
                    data.hex()
                )
            return None, None, None
        # frame control bits
        framectrl, = struct.unpack('>H', data[xiaomi_index + 3:xiaomi_index + 5])
        # check data is present
        if not (framectrl & 0x4000):
            return {
                "rssi": rssi,
                "mac": ''.join('{:02X}'.format(x) for x in xiaomi_mac_reversed[::-1]),
                "type": sensor_type,
                "packet": packet_id,
                "data": False,
            }, None, None
            # return None
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
            return None, None, None
        xdata_point += xiaomi_index + 14
        # check if xiaomi data start and length is valid
        if xdata_length != len(data[xdata_point:-1]):
            return None, None, None
        # check encrypted data flags
        if framectrl & 0x0800:
            # try to find encryption key for current device
            try:
                key = self.aeskeys[xiaomi_mac_reversed]
            except KeyError:
                # no encryption key found
                return None, None, None
            nonce = b"".join(
                [
                    xiaomi_mac_reversed,
                    data[xiaomi_index + 5:xiaomi_index + 7],
                    data[xiaomi_index + 7:xiaomi_index + 8]
                ]
            )
            encrypted_payload = data[xdata_point:msg_length - 1]
            aad = b"\x11"
            token = encrypted_payload[-4:]
            payload_counter = encrypted_payload[-7:-4]
            nonce = b"".join([nonce, payload_counter])
            cipherpayload = encrypted_payload[:-7]
            cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
            cipher.update(aad)
            decrypted_payload = None
            try:
                decrypted_payload = cipher.decrypt_and_verify(cipherpayload, token)
            except ValueError as error:
                _LOGGER.error("Decryption failed: %s", error)
                _LOGGER.error("token: %s", token.hex())
                _LOGGER.error("nonce: %s", nonce.hex())
                _LOGGER.error("encrypted_payload: %s", encrypted_payload.hex())
                _LOGGER.error("cipherpayload: %s", cipherpayload.hex())
                return None, None, None
            if decrypted_payload is None:
                _LOGGER.error(
                    "Decryption failed for %s, decrypted payload is None",
                    "".join("{:02X}".format(x) for x in xiaomi_mac_reversed[::-1]),
                )
                return None, None, None
            # replace cipher with decrypted data
            msg_length -= len(data[xdata_point:msg_length - 1])
            data = b"".join((data[:xdata_point], decrypted_payload, data[-1:]))
            msg_length += len(decrypted_payload)
        result = {
            "rssi": rssi,
            "mac": ''.join('{:02X}'.format(x) for x in xiaomi_mac_reversed[::-1]),
            "type": sensor_type,
            "packet": packet_id,
            "data": True,
        }
        binary = False
        measuring = False
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
            resfunc, tbinary, tmeasuring = self._dataobject_dict.get(xvalue_typecode, (None, None, None))
            if resfunc:
                binary = binary or tbinary
                measuring = measuring or tmeasuring
                result.update(resfunc(xvalue))
            else:
                if self.report_unknown:
                    _LOGGER.info(
                        "UNKNOWN dataobject from DEVICE: %s, MAC: %s, ADV: %s",
                        sensor_type,
                        ''.join('{:02X}'.format(x) for x in xiaomi_mac_reversed[::-1]),
                        data.hex()
                    )
            if xnext_point > msg_length - 3:
                break
            xdata_point = xnext_point
        binary = binary and binary_data
        return result, binary, measuring
