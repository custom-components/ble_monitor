"""Xiaomi passive BLE monitor integration."""
import asyncio
from datetime import timedelta
import logging
import queue
import statistics as sts
import struct
from threading import Thread
#from time import sleep

import aioblescan as aiobs
from Cryptodome.Cipher import AES
import voluptuous as vol

from homeassistant.const import (
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_BATTERY,
    EVENT_HOMEASSISTANT_STOP,
    TEMP_CELSIUS,
    ATTR_BATTERY_LEVEL,
    STATE_OFF, STATE_ON,
)

# Binary Sensor Class will be renamed in the future HA releases
try:
    from homeassistant.components.binary_sensor import BinarySensorEntity
except ImportError:
    from homeassistant.components.binary_sensor import BinarySensorDevice as BinarySensorEntity

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_point_in_utc_time
import homeassistant.util.dt as dt_util

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
    DEFAULT_WHITELIST,
    CONF_ROUNDING,
    CONF_DECIMALS,
    CONF_PERIOD,
    CONF_LOG_SPIKES,
    CONF_USE_MEDIAN,
    CONF_ACTIVE_SCAN,
    CONF_HCI_INTERFACE,
    CONF_BATT_ENTITIES,
    CONF_ENCRYPTORS,
    CONF_REPORT_UNKNOWN,
    CONF_WHITELIST,
    CONF_TMIN,
    CONF_TMAX,
    CONF_HMIN,
    CONF_HMAX,
    XIAOMI_TYPE_DICT,
    MMTS_DICT,
    SW_CLASS_DICT,
    CN_NAME_DICT,
)

_LOGGER = logging.getLogger(__name__)

# regex constants for configuration schema
MAC_REGEX = "(?i)^(?:[0-9A-F]{2}[:]){5}(?:[0-9A-F]{2})$"
AES128KEY_REGEX = "(?i)^[A-F0-9]{32}$"

ENCRYPTORS_LIST_SCHEMA = vol.Schema(
    {
        cv.matches_regex(MAC_REGEX): cv.matches_regex(AES128KEY_REGEX)
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
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
        vol.Optional(CONF_BATT_ENTITIES, default=DEFAULT_BATT_ENTITIES): cv.boolean,
        vol.Optional(CONF_ENCRYPTORS, default={}): ENCRYPTORS_LIST_SCHEMA,
        vol.Optional(CONF_REPORT_UNKNOWN, default=DEFAULT_REPORT_UNKNOWN): cv.boolean,
        vol.Optional(
            CONF_WHITELIST, default=DEFAULT_WHITELIST
        ): vol.Any(vol.All(cv.ensure_list, [cv.matches_regex(MAC_REGEX)]), cv.boolean),
    }
)

# Structured objects for data conversions
TH_STRUCT = struct.Struct("<hH")
H_STRUCT = struct.Struct("<H")
T_STRUCT = struct.Struct("<h")
CND_STRUCT = struct.Struct("<H")
ILL_STRUCT = struct.Struct("<I")
FMDH_STRUCT = struct.Struct("<H")


class HCIdump(Thread):
    """Mimic deprecated hcidump tool."""

    def __init__(self, config, dataqueue):
        """Initiate HCIdump thread."""
        Thread.__init__(self)
        _LOGGER.debug("HCIdump thread: Init")
        self.lpacket_id = {}
        self._event_loop = None
        self._interfaces = config[CONF_HCI_INTERFACE]
        self._active = config[CONF_ACTIVE_SCAN]
        self.report_unknown = config[CONF_REPORT_UNKNOWN]
        self.dataqueue = dataqueue
        _LOGGER.debug("HCIdump thread: Init finished")

    def run(self):
        """Run HCIdump thread."""
        _LOGGER.debug("HCIdump thread: Run")
        mysocket = {}
        fac = {}
        conn = {}
        btctrl = {}
        self._event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)
        for hci in self._interfaces:
            try:
                mysocket[hci] = aiobs.create_bt_socket(hci)
            except OSError as error:
                _LOGGER.error("HCIdump thread: OS error: %s", error)
            else:
                fac[hci] = self._event_loop._create_connection_transport(
                    mysocket[hci], aiobs.BLEScanRequester, None, None
                )
                _LOGGER.debug("HCIdump thread: Connection to hci%i", hci)
                conn[hci], btctrl[hci] = self._event_loop.run_until_complete(fac[hci])
                _LOGGER.debug("HCIdump thread: Connected to hci%i", hci)
                btctrl[hci].process = self.filter_and_queue
                btctrl[hci].send_command(
                    aiobs.HCI_Cmd_LE_Set_Scan_Params(scan_type=self._active)
                )
                btctrl[hci].send_scan_request()
        _LOGGER.debug("HCIdump thread: start main event_loop")
        try:
            self._event_loop.run_forever()
        finally:
            _LOGGER.debug("HCIdump thread: main event_loop stopped, finishing")
            for hci in self._interfaces:
                btctrl[hci].stop_scan_request()
                conn[hci].close()
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
    
    def filter_and_queue(self, data):
        """Filter hci events"""
        if data is None:
            return None
        # check for Xiaomi service data
        xiaomi_index = data.find(b'\x16\x95\xFE', 15)
        if xiaomi_index == -1:
            return None
        # check for no BR/EDR + LE General discoverable mode flags
        adv_index = data.find(b"\x02\x01\x06", 14, 17)
        if adv_index == -1:
            return None
        # check for BTLE msg size
        msg_length = data[2] + 3
        if msg_length != len(data):
            return None
        # check for MAC presence in message and in service data
        xiaomi_mac_reversed = data[xiaomi_index + 8:xiaomi_index + 14]
        source_mac_reversed = data[adv_index - 7:adv_index - 1]
        if xiaomi_mac_reversed != source_mac_reversed:
            return None
        # frame control bits
        framectrl, = struct.unpack('>H', data[xiaomi_index + 3:xiaomi_index + 5])
        # check data is present
        if not (framectrl & 0x4000):
            return None
        self.dataqueue.put(data)




class BLEScanner:
    """BLE scanner."""

    def __init__(self, config):
        """Init"""
        self.hcidump_data = []
        self.dataqueue = queue.Queue()
        self.dumpthread = None
        self.config = config

    def start(self):
        """Start receiving broadcasts."""
        self.hcidump_data.clear()
        _LOGGER.debug("Spawning HCIdump thread(s).")
        self.dumpthread = HCIdump(
            config = self.config,
            dataqueue = self.dataqueue,
        )
        self.dumpthread.start()

    def stop(self):
        """Stop HCIdump thread(s)."""
        result = True
        if self.dumpthread.isAlive():
            self.dumpthread.join()
            if self.dumpthread.isAlive():
                result = False
                _LOGGER.error(
                        "Waiting for the HCIdump thread to finish took too long! (>10s)"
                )
        return result

    def shutdown_handler(self, event):
        """Run homeassistant_stop event handler."""
        _LOGGER.debug("Running homeassistant_stop event handler: %s", event)
        self.stop()
        self.dataqueue.put(None)

class Updater:
    """Entities updater"""

    def __init__(self, dataqueue, config, add_entities):

        def reverse_mac(rmac):
            """Change LE order to BE."""
            if len(rmac) != 12:
                return None
            return rmac[10:12] + rmac[8:10] + rmac[6:8] + rmac[4:6] + rmac[2:4] + rmac[0:2]

        self.dataqueue = dataqueue
        self.config = config
        self.log_spikes = config[CONF_LOG_SPIKES]
        self.period = config[CONF_PERIOD]
        self.batt_entities = config[CONF_BATT_ENTITIES]
        self.report_unknown = config[CONF_REPORT_UNKNOWN]
        self.aeskeyslist = {}
        for mac in config[CONF_ENCRYPTORS]:
            p_mac = bytes.fromhex(reverse_mac(mac.replace(":", "")).lower())
            p_key = bytes.fromhex(config[CONF_ENCRYPTORS][mac].lower())
            self.aeskeyslist[p_mac] = p_key
        _LOGGER.debug("%s encryptors mac:key pairs loaded.", len(self.aeskeyslist))
        self.whitelist = []
        if isinstance(config[CONF_WHITELIST], bool):
            if config[CONF_WHITELIST] is True:
                for mac in config[CONF_ENCRYPTORS]:
                    self.whitelist.append(mac)
        if isinstance(config[CONF_WHITELIST], list):
            for mac in config[CONF_WHITELIST]:
                self.whitelist.append(mac)
            for mac in config[CONF_ENCRYPTORS]:
                self.whitelist.append(mac)
        for i, mac in enumerate(self.whitelist):
            self.whitelist[i] = bytes.fromhex(reverse_mac(mac.replace(":", "")).lower())
        _LOGGER.debug("%s whitelist item(s) loaded.", len(self.whitelist))
        self.add_entities = add_entities

    def datacollector(self, event):
        """Collect data from queue"""

        def parse_raw_message(data):
            """Parse the raw data."""
            # check for Xiaomi service data
            xiaomi_index = data.find(b'\x16\x95\xFE', 15)
            msg_length = data[2] + 3
            xiaomi_mac_reversed = data[xiaomi_index + 8:xiaomi_index + 14]
            framectrl, = struct.unpack('>H', data[xiaomi_index + 3:xiaomi_index + 5])
            try:
                sensor_type = XIAOMI_TYPE_DICT[
                    data[xiaomi_index + 5:xiaomi_index + 7]
                ]
            except KeyError:
                if self.report_unknown:
                    (rssi,) = struct.unpack("<b", data[msg_length - 1:msg_length])
                    #strange positive RSSI workaround
                    if rssi > 0:
                        rssi = -rssi
                    _LOGGER.info(
                        "BLE ADV from UNKNOWN: RSSI: %s, MAC: %s, ADV: %s",
                        rssi,
                        ''.join('{:02X}'.format(x) for x in xiaomi_mac_reversed[::-1]),
                        data.hex()
                    )
                return None
            # check for MAC presence in whitelist, if needed
            if self.whitelist:
                if xiaomi_mac_reversed not in self.whitelist:
                    return None
            packet_id = data[xiaomi_index + 7]
            try:
                prev_packet = parse_raw_message.lpacket_id[xiaomi_mac_reversed]
            except KeyError:
                prev_packet = None
            if prev_packet == packet_id:
                # _LOGGER.debug("DUPLICATE: %s, IGNORING!", data)
                return None
            parse_raw_message.lpacket_id[xiaomi_mac_reversed] = packet_id
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
                    key = self.aeskeyslist[xiaomi_mac_reversed]
                except KeyError:
                    # no encryption key found
                    return None
                encrypted_payload = data[xdata_point:msg_length-1]
                token = encrypted_payload[-4:]
                payload_counter = encrypted_payload[-7:-4]
                nonce = b"".join(
                    [
                        xiaomi_mac_reversed,
                        data[xiaomi_index + 5:xiaomi_index + 7],
                        data[xiaomi_index + 7:xiaomi_index + 8],
                        payload_counter
                    ]
                )
                cipherpayload = encrypted_payload[:-7]
                cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
                cipher.update(b"\x11")
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
                #return plaindata
                if plaindata is None:
                    _LOGGER.error(
                        "Decryption failed for %s, decrypted payload is None",
                        "".join("{:02X}".format(x) for x in xiaomi_mac_reversed[::-1]),
                    )
                    return None
                # replace cipher with decrypted data
                msg_length -= len(data[xdata_point:msg_length-1])
                data = b"".join((data[:xdata_point], plaindata, data[-1:]))
                msg_length += len(plaindata)
            # extract RSSI byte
            (rssi,) = struct.unpack("<b", data[msg_length - 1:msg_length])
            #strange positive RSSI workaround
            if rssi > 0:
                rssi = -rssi
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
                #res = self.parse_xiaomi_value(xvalue, xvalue_typecode)
                res = None
                vlength = len(xvalue)
                if vlength == 4:
                    if xvalue_typecode == b'\x0D\x10':
                        (temp, humi) = TH_STRUCT.unpack(xvalue)
                        res =  {"temperature": temp / 10, "humidity": humi / 10}
                elif vlength == 2:
                    if xvalue_typecode == b'\x06\x10':
                        (humi,) = H_STRUCT.unpack(xvalue)
                        res =  {"humidity": humi / 10}
                    elif xvalue_typecode == b'\x04\x10':
                        (temp,) = T_STRUCT.unpack(xvalue)
                        res =  {"temperature": temp / 10}
                    elif xvalue_typecode == b'\x09\x10':
                        (cond,) = CND_STRUCT.unpack(xvalue)
                        res =  {"conductivity": cond}
                    elif xvalue_typecode == b'\x10\x10':
                        (fmdh,) = FMDH_STRUCT.unpack(xvalue)
                        res =  {"formaldehyde": fmdh / 100}
                elif vlength == 1:
                    if xvalue_typecode == b'\x0A\x10':
                        res =  {"battery": xvalue[0]}
                    elif xvalue_typecode == b'\x08\x10':
                        res =  {"moisture": xvalue[0]}
                    elif xvalue_typecode == b'\x12\x10':
                        res =  {"switch": xvalue[0]}
                    elif xvalue_typecode == b'\x13\x10':
                        res =  {"consumable": xvalue[0]}
                elif vlength == 3:
                    if xvalue_typecode == b'\x07\x10':
                        (illum,) = ILL_STRUCT.unpack(xvalue + b'\x00')
                        res =  {"illuminance": illum}
                if res:
                    result.update(res)
                if xnext_point > msg_length - 3:
                    break
                xdata_point = xnext_point
            return result
        
        parse_raw_message.lpacket_id = {}

        data = {}
        sensors_by_mac = {}
        batt = {}
        qcounter = 0
        ts_last = dt_util.now()
        ts_now = ts_last
        while True:
            try:
                hcievent = self.dataqueue.get(block = True, timeout = 1)
                if hcievent is None:
                   _LOGGER.debug("Updater stopped.")
                   return True
                data = parse_raw_message(hcievent)
            except queue.Empty:
                pass
            if data:
                qcounter += 1
                mac = data["mac"]
                devicetype = data["type"]
                batt_attr = None
                # fixed entity index for every measurement type
                # according to the sensor implementation
                t_i, h_i, m_i, c_i, i_i, f_i, cn_i, sw_i, b_i = MMTS_DICT[devicetype]
                if mac not in sensors_by_mac:
                    sensors = []
                    if t_i != 9:
                        sensors.insert(t_i, TemperatureSensor(mac, devicetype, self.config))
                    if h_i != 9:
                        sensors.insert(h_i, HumiditySensor(mac, devicetype, self.config))
                    if m_i != 9:
                        sensors.insert(m_i, MoistureSensor(mac, devicetype, self.config))
                    if c_i != 9:
                        sensors.insert(c_i, ConductivitySensor(mac, devicetype, self.config))
                    if i_i != 9:
                        sensors.insert(i_i, IlluminanceSensor(mac, devicetype, self.config))
                    if f_i != 9:
                        sensors.insert(f_i, FormaldehydeSensor(mac, devicetype, self.config))
                    if cn_i != 9:
                        sensors.insert(cn_i, ConsumableSensor(mac, devicetype, self.config))
                        try:
                            setattr(sensors[cn_i], "_cn_name", CN_NAME_DICT[devicetype])
                        except KeyError:
                            pass
                    if sw_i != 9:
                        sensors.insert(sw_i, SwitchBinarySensor(mac, devicetype))
                        try:
                            setattr(sensors[sw_i], "_swclass", SW_CLASS_DICT[devicetype])
                        except KeyError:
                            pass
                    if self.batt_entities and (b_i != 9):
                        sensors.insert(b_i, BatterySensor(mac, devicetype, self.config))
                    sensors_by_mac[mac] = sensors
                    self.add_entities(sensors)
                else:
                    sensors = sensors_by_mac[mac]
                # store found readings per entity
                if (b_i != 9):
                    if "battery" in data:
                        batt[mac] = int(data["battery"])
                        batt_attr = batt[mac]
                        if self.batt_entities:
                            sensors[b_i].collect(data)
                    else:
                        try:
                            batt_attr = batt[mac]
                        except KeyError:
                            batt_attr = None                        
                if "switch" in data:
                    sensors[sw_i].collect(data, batt_attr)
                    if sensors[sw_i].pending_update:
                        sensors[sw_i].schedule_update_ha_state(True)
                if "temperature" in data:
                    if CONF_TMAX >= data["temperature"] >= CONF_TMIN:
                        sensors[t_i].collect(data, batt_attr)
                    elif self.log_spikes:
                        _LOGGER.error(
                            "Temperature spike: %s (%s)",
                            data["temperature"],
                            mac,
                        )
                if "humidity" in data:
                    if CONF_HMAX >= data["humidity"] >= CONF_HMIN:
                        sensors[h_i].collect(data, batt_attr)
                    elif self.log_spikes:
                        _LOGGER.error(
                            "Humidity spike: %s (%s)", data["humidity"], mac,
                        )
                if "conductivity" in data:
                    sensors[c_i].collect(data, batt_attr)
                if "moisture" in data:
                    sensors[m_i].collect(data, batt_attr)
                if "illuminance" in data:
                    sensors[i_i].collect(data, batt_attr)
                if "formaldehyde" in data:
                    sensors[f_i].collect(data, batt_attr)
                if "consumable" in data:
                    sensors[cn_i].collect(data, batt_attr)
                data.clear()

            ts_now = dt_util.now()
            if ts_now - ts_last < timedelta(seconds = self.period):
                continue
            else:
                ts_last = ts_now
                #force_binary_only = False
            maccount = 0
            for mac, elist in sensors_by_mac.items():
                maccount += 1
                for entity in elist:
                    if entity.pending_update:
                        entity.schedule_update_ha_state(True)

            _LOGGER.debug(
                "%i Xiaomi BLE ADV messages processed for %i xiaomi device(s).",
                qcounter,
                maccount
            )
            qcounter = 0

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""

    _LOGGER.debug("Starting")
    if config[CONF_REPORT_UNKNOWN]:
        _LOGGER.info(
            "Attention! Option report_unknown is enabled, be ready for a huge output..."
        )
    # prepare device:key list to speedup parser
    scanner = BLEScanner(config)
    hass.bus.listen(EVENT_HOMEASSISTANT_STOP, scanner.shutdown_handler)
    updater = Updater(scanner.dataqueue, config, add_entities)
    track_point_in_utc_time(
        hass,
        updater.datacollector,
        dt_util.utcnow() + timedelta(seconds=1)
    )
    scanner.start()
    # Return successful setup
    return True


class MeasuringSensor(Entity):
    """Base class for measuring sensor entity"""

    def __init__(self, devicetype, config):
        """Initialize the sensor."""
        self._state = None
        #self._battery = None
        self._device_state_attributes = {}
        self._unique_id = ""
        self._measurements = []
        self._measurement = "measurement"
        self._devicetype = devicetype
        self.pending_update = False
        self._rdecimals = config[CONF_DECIMALS]
        self._rounding = config[CONF_ROUNDING]
        self._usemedian = config[CONF_USE_MEDIAN]
        self._fdec = 0
    
    @property
    def name(self):
        """Return the name of the sensor."""
        return "mi {}".format(self._unique_id)
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._device_state_attributes
    
    @property
    def should_poll(self):
        """No polling needed."""
        return False
    
    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._unique_id

    @property
    def force_update(self):
        """Force update."""
        return True

    def collect(self, data, batt_attr = None):
        """Measurements collector"""
        self._measurements.append(data[self._measurement])
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["rssi"] = data["rssi"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True
    
    def update(self):
        """updates sensor state and attributes"""
        textattr = ""
        err = None
        rdecimals = self._rdecimals
        # formaldehyde decimals workaround
        if self._fdec > 0:
                rdecimals = self._fdec
        # LYWSD03MMC "jagged" humidity workaround
        if self._devicetype == "LYWSD03MMC":
            measurements = [int(item) for item in self._measurements]
        else:
            measurements = self._measurements
        try:
            if self._rounding:
                state_median = round(
                    sts.median(measurements), rdecimals
                )
                state_mean = round(
                    sts.mean(measurements), rdecimals
                )
            else:
                state_median = sts.median(measurements)
                state_mean = sts.mean(measurements)
            if self._usemedian:
                textattr = "last median of"
                self._state = state_median
            else:
                textattr = "last mean of"
                self._state = state_mean
            self._device_state_attributes[textattr] = len(measurements)
            self._device_state_attributes["median"] = state_median
            self._device_state_attributes["mean"] = state_mean
        except AttributeError:
            _LOGGER.debug("Sensor %s not yet ready for update", self.name)
        except ZeroDivisionError as err:
            pass
        except IndexError as err:
            pass
        except RuntimeError as err:
            pass
        if err:
            _LOGGER.error("Sensor %s (%s) update error:", self.name, self._devicetype)
            _LOGGER.error(err)
        self._measurements.clear()
        self.pending_update = False

class SwitchingSensor(BinarySensorEntity):
    """Base class for switching sensor entity"""

    def __init__(self, devicetype):
        """Initialize the sensor."""
        self._state = None
        self._swclass = None
        #self._battery = None
        self._device_state_attributes = {}
        self._devicetype = devicetype
        self._newstate = None
        self.prev_state = None
        self.pending_update = False

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return bool(self._state)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "mi {}".format(self._unique_id)

    @property
    def state(self):
        """Return the state of the binary sensor."""
        return STATE_ON if self.is_on else STATE_OFF

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._device_state_attributes

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return self._swclass

    @property
    def force_update(self):
        """Force update."""
        return True

    def collect(self, data, batt_attr = None):
        """Measurements collector"""
        self._newstate = data["switch"]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["rssi"] = data["rssi"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        if self._newstate != self.prev_state:
            self.pending_update = True

    def update(self):
        """updates sensor state and attributes"""
        self.prev_state = self._state
        self._state = self._newstate
        self.pending_update = False

class TemperatureSensor(MeasuringSensor):
    """Representation of a sensor."""

    def __init__(self, mac, devicetype, config):
        """Initialize the sensor."""
        super().__init__(devicetype, config)
        self._unique_id = "t_" + mac
        self._measurement = "temperature"
    
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_TEMPERATURE

class HumiditySensor(MeasuringSensor):
    """Representation of a sensor."""

    def __init__(self, mac, devicetype, config):
        """Initialize the sensor."""
        super().__init__(devicetype, config)
        self._unique_id = "h_" + mac
        self._measurement = "humidity"
    
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_HUMIDITY

class MoistureSensor(MeasuringSensor):
    """Representation of a sensor."""

    def __init__(self, mac, devicetype, config):
        """Initialize the sensor."""
        super().__init__(devicetype, config)
        self._unique_id = "m_" + mac
        self._measurement = "moisture"
    
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_HUMIDITY

class ConductivitySensor(MeasuringSensor):
    """Representation of a sensor."""

    def __init__(self, mac, devicetype, config):
        """Initialize the sensor."""
        super().__init__(devicetype, config)
        self._unique_id = "c_" + mac
        self._measurement = "conductivity"
    
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "µS/cm"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:flash-circle"

class IlluminanceSensor(MeasuringSensor):
    """Representation of a sensor."""

    def __init__(self, mac, devicetype, config):
        """Initialize the sensor."""
        super().__init__(devicetype, config)
        self._unique_id = "l_" + mac
        self._measurement = "illuminance"
    
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "lx"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:white-balance-sunny"

class FormaldehydeSensor(MeasuringSensor):
    """Representation of a sensor."""

    def __init__(self, mac, devicetype, config):
        """Initialize the sensor."""
        super().__init__(devicetype, config)
        self._unique_id = "f_" + mac
        self._measurement = "formaldehyde"
        self._fdec = 2
    
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "mg/m³"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:chemical-weapon"

class BatterySensor(MeasuringSensor):
    """Representation of a sensor."""

    def __init__(self, mac, devicetype, config):
        """Initialize the sensor."""
        super().__init__(devicetype, config)
        self._unique_id = "batt_" + mac
        self._measurement = "battery"
    
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_BATTERY

    def collect(self, data, batt_attr = None):
        """Measurements collector"""
        self._state = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["rssi"] = data["rssi"]
        self.pending_update = True
    
    def update(self):
        self.pending_update = False

class ConsumableSensor(MeasuringSensor):
    """Representation of a sensor."""

    def __init__(self, mac, devicetype, config):
        """Initialize the sensor."""
        super().__init__(devicetype, config)
        self._cn_name = "cn_"
        self._nmac = mac
        self._measurement = "consumable"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._cn_name + self._nmac
    
    @property
    def name(self):
        """Return the name of the sensor."""
        return "mi {}".format(self._cn_name + self._nmac)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:mdi-recycle-variant"

    def collect(self, data, batt_attr = None):
        """Measurements collector"""
        self._state = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["rssi"] = data["rssi"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True
    
    def update(self):
        self.pending_update = False

class SwitchBinarySensor(SwitchingSensor):
    """Representation of a Sensor."""

    def __init__(self, mac, devicetype):
        """Initialize the sensor."""
        super().__init__(devicetype)
        self._unique_id = "sw_" + mac
