"""Xiaomi passive BLE monitor integration."""
import asyncio
from datetime import timedelta
import logging
import statistics as sts
import struct
from threading import Thread
from time import sleep

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

    def __init__(self, config, dumplist, lpacket_cntr):
        """Initiate HCIdump thread."""
        Thread.__init__(self)
        _LOGGER.debug("HCIdump thread: Init")
        self.dumplist = dumplist
        self.lpacket_cntr = lpacket_cntr
        self._event_loop = None
        self._interfaces = config[CONF_HCI_INTERFACE]
        self._active = config[CONF_ACTIVE_SCAN]
        self.report_unknown = config[CONF_REPORT_UNKNOWN]
        self.aeskeyslist = {}
        for mac in config[CONF_ENCRYPTORS]:
            p_mac = bytes.fromhex(self.reverse_mac(mac.replace(":", "")).lower())
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
            self.whitelist[i] = bytes.fromhex(self.reverse_mac(mac.replace(":", "")).lower())
        _LOGGER.debug("%s whitelist item(s) loaded.", len(self.whitelist))
        _LOGGER.debug("HCIdump thread: Init finished")

    @classmethod
    def reverse_mac(cls, rmac):
        """Change LE order to BE."""
        if len(rmac) != 12:
            return None
        return rmac[10:12] + rmac[8:10] + rmac[6:8] + rmac[4:6] + rmac[2:4] + rmac[0:2]

    def process_hci_events(self, data):
        """Collect HCI events."""
        packet = self.parse_raw_message(data)
        if packet is not None:
            self.dumplist.append(packet)

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
                _LOGGER.debug("HCIdump thread: Connection")
                conn[hci], btctrl[hci] = self._event_loop.run_until_complete(fac[hci])
                _LOGGER.debug("HCIdump thread: Connected")
                btctrl[hci].process = self.process_hci_events
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

    def lpacket(self, mac, packet=None):
        """Last_packet static storage."""
        if packet is not None:
            self.lpacket_cntr[mac] = packet
        else:
            try:
                cntr = self.lpacket_cntr[mac]
            except KeyError:
                cntr = None
            return cntr

    @classmethod
    def parse_xiaomi_value(cls, hexvalue, typecode):
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

    @classmethod
    def decrypt_payload(cls, encrypted_payload, key, nonce):
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

    def parse_raw_message(self, data):
        """Parse the raw data."""
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
        # frame control bits
        framectrl, = struct.unpack('>H', data[xiaomi_index + 3:xiaomi_index + 5])
        # check data is present
        if not (framectrl & 0x4000):
            return None
        packet_id = data[xiaomi_index + 7]
        prev_packet = self.lpacket(mac=xiaomi_mac_reversed)
        if prev_packet == packet_id:
            # _LOGGER.debug("DUPLICATE: %s, IGNORING!", data)
            return None
        self.lpacket(xiaomi_mac_reversed, packet_id)
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
            nonce = b"".join(
                [
                    xiaomi_mac_reversed,
                    data[xiaomi_index + 5:xiaomi_index + 7],
                    data[xiaomi_index + 7:xiaomi_index + 8]
                ]
            )
            decrypted_payload = self.decrypt_payload(
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
            res = self.parse_xiaomi_value(xvalue, xvalue_typecode)
            if res:
                result.update(res)
            if xnext_point > msg_length - 3:
                break
            xdata_point = xnext_point
        return result


class BLEScanner:
    """BLE scanner."""

    def __init__(self):
        """Init"""
        self.hcidump_data = []
        self.lpacket_cntr = {}
        self.dumpthread = None

    def start(self, config):
        """Start receiving broadcasts."""
        self.hcidump_data.clear()
        _LOGGER.debug("Spawning HCIdump thread(s).")
        self.dumpthread = HCIdump(
            config = config,
            dumplist = self.hcidump_data,
            lpacket_cntr=self.lpacket_cntr
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


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""

    def lpacket(mac, packet=None):
        """Last_packet static storage."""
        if packet is not None:
            lpacket.cntr[mac] = packet
        else:
            try:
                cntr = lpacket.cntr[mac]
            except KeyError:
                cntr = None
            return cntr

    _LOGGER.debug("Starting")
    sensors_by_mac = {}
    lpacket.cntr = {}
    if config[CONF_REPORT_UNKNOWN]:
        _LOGGER.info(
            "Attention! Option report_unknown is enabled, be ready for a huge output..."
        )
    # prepare device:key list to speedup parser
    firstrun = True
    scanner = BLEScanner()
    hass.bus.listen(EVENT_HOMEASSISTANT_STOP, scanner.shutdown_handler)
    scanner.start(config)
    sleep(1)

    def calc_update_state(
        entity_to_update, sensor_mac, config, measurements_list, stype=None, fdec = 0
    ):
        """Averages according to options and updates the entity state."""
        textattr = ""
        success = False
        error = ""
        rdecimals = config[CONF_DECIMALS]
        # formaldehyde decimals workaround
        if fdec > 0:
            rdecimals = fdec
        # LYWSD03MMC "jagged" humidity workaround
        if stype == "LYWSD03MMC":
            measurements = [int(item) for item in measurements_list]
        else:
            measurements = measurements_list
        try:
            if config[CONF_ROUNDING]:
                state_median = round(
                    sts.median(measurements), rdecimals
                )
                state_mean = round(
                    sts.mean(measurements), rdecimals
                )
            else:
                state_median = sts.median(measurements)
                state_mean = sts.mean(measurements)
            if config[CONF_USE_MEDIAN]:
                textattr = "last median of"
                setattr(entity_to_update, "_state", state_median)
            else:
                textattr = "last mean of"
                setattr(entity_to_update, "_state", state_mean)
            getattr(entity_to_update, "_device_state_attributes")[textattr] = len(
                measurements
            )
            getattr(entity_to_update, "_device_state_attributes")[
                "median"
            ] = state_median
            getattr(entity_to_update, "_device_state_attributes")["mean"] = state_mean
            entity_to_update.schedule_update_ha_state()
            success = True
        except AttributeError:
            _LOGGER.debug("Sensor %s not yet ready for update", sensor_mac)
            success = True
        except ZeroDivisionError as err:
            error = err
        except IndexError as err:
            error = err
        except RuntimeError as err:
            error = err
        return success, error

    def discover_ble_devices(config):
        """Discover Bluetooth LE devices."""
        nonlocal firstrun
        if firstrun:
            firstrun = False
            _LOGGER.debug("First run, skip parsing.")
            return []
        _LOGGER.debug("Discovering Bluetooth LE devices")
        log_spikes = config[CONF_LOG_SPIKES]
        _LOGGER.debug("Time to analyze...")
        stype = {}
        hum_m_data = {}
        temp_m_data = {}
        illum_m_data = {}
        moist_m_data = {}
        cond_m_data = {}
        formaldehyde_m_data = {}
        cons_m_data = {}
        switch_m_data = {}
        batt = {}  # battery
        rssi = {}
        macs = {}  # all found macs
        _LOGGER.debug("Getting data from HCIdump thread")
        jres = scanner.stop()
        if jres is False:
            _LOGGER.error("HCIdump thread is not completed, interrupting data processing!")
            return []
        hcidump_raw = [*scanner.hcidump_data]
        scanner.start(config)  # minimum delay between HCIdumps
        ###report_unknown = config[CONF_REPORT_UNKNOWN]
        for data in hcidump_raw:
            ###data = parse_raw_message(msg, aeskeyslist, whitelist, report_unknown)
            # ignore duplicated message
            packet = data["packet"]
            mac = data["mac"]
            prev_packet = lpacket(mac)
            if prev_packet == packet:
                _LOGGER.error("DUPLICATE: %s, IGNORING!", data)
                continue
            lpacket(mac, packet)
            # store found readings per device
            if "switch" in data:
                switch_m_data[mac] = int(data["switch"])
                macs[mac] = mac
            if "temperature" in data:
                if CONF_TMAX >= data["temperature"] >= CONF_TMIN:
                    if mac not in temp_m_data:
                        temp_m_data[mac] = []
                    temp_m_data[mac].append(data["temperature"])
                    macs[mac] = mac
                elif log_spikes:
                    _LOGGER.error(
                        "Temperature spike: %s (%s)",
                        data["temperature"],
                        mac,
                    )
            if "humidity" in data:
                if CONF_HMAX >= data["humidity"] >= CONF_HMIN:
                    if mac not in hum_m_data:
                        hum_m_data[mac] = []
                    hum_m_data[mac].append(data["humidity"])
                    macs[mac] = mac
                elif log_spikes:
                    _LOGGER.error(
                        "Humidity spike: %s (%s)", data["humidity"], mac,
                    )
            if "conductivity" in data:
                if mac not in cond_m_data:
                    cond_m_data[mac] = []
                cond_m_data[mac].append(data["conductivity"])
                macs[mac] = mac
            if "moisture" in data:
                if mac not in moist_m_data:
                    moist_m_data[mac] = []
                moist_m_data[mac].append(data["moisture"])
                macs[mac] = mac
            if "illuminance" in data:
                if mac not in illum_m_data:
                    illum_m_data[mac] = []
                illum_m_data[mac].append(data["illuminance"])
                macs[mac] = mac
            if "formaldehyde" in data:
                if mac not in formaldehyde_m_data:
                    formaldehyde_m_data[mac] = []
                formaldehyde_m_data[mac].append(data["formaldehyde"])
                macs[mac] = mac
            if "consumable" in data:
                cons_m_data[mac] = int(data["consumable"])
                macs[mac] = mac
            if "battery" in data:
                batt[mac] = int(data["battery"])
                macs[mac] = mac
            if mac not in rssi:
                rssi[mac] = []
            rssi[mac].append(int(data["rssi"]))
            stype[mac] = data["type"]

        # for every seen device
        for mac in macs:
            # fixed entity index for every measurement type
            # according to the sensor implementation
            sensortype = stype[mac]
            t_i, h_i, m_i, c_i, i_i, f_i, cn_i, sw_i, b_i = MMTS_DICT[sensortype]
            # if necessary, create a list of entities
            # according to the sensor implementation

            if mac in sensors_by_mac:
                sensors = sensors_by_mac[mac]
            else:
                sensors = []
                if t_i != 9:
                    sensors.insert(t_i, TemperatureSensor(mac))
                if h_i != 9:
                    sensors.insert(h_i, HumiditySensor(mac))
                if m_i != 9:
                    sensors.insert(m_i, MoistureSensor(mac))
                if c_i != 9:
                    sensors.insert(c_i, ConductivitySensor(mac))
                if i_i != 9:
                    sensors.insert(i_i, IlluminanceSensor(mac))
                if f_i != 9:
                    sensors.insert(f_i, FormaldehydeSensor(mac))
                if cn_i != 9:
                    sensors.insert(cn_i, ConsumableSensor(mac))
                    try:
                        setattr(sensors[cn_i], "_cn_name", CN_NAME_DICT[sensortype])
                    except KeyError:
                        pass
                if sw_i != 9:
                    sensors.insert(sw_i, SwitchBinarySensor(mac))
                    try:
                        setattr(sensors[sw_i], "_swclass", SW_CLASS_DICT[sensortype])
                    except KeyError:
                        pass
                if config[CONF_BATT_ENTITIES] and (b_i != 9):
                    sensors.insert(b_i, BatterySensor(mac))
                sensors_by_mac[mac] = sensors
                add_entities(sensors)
            # append joint attributes
            for sensor in sensors:
                getattr(sensor, "_device_state_attributes")["last packet id"] = lpacket(
                    mac
                )
                getattr(sensor, "_device_state_attributes")["rssi"] = round(
                    sts.mean(rssi[mac])
                )
                getattr(sensor, "_device_state_attributes")["sensor type"] = sensortype
                if not isinstance(sensor, BatterySensor) and mac in batt:
                    getattr(sensor, "_device_state_attributes")[
                        ATTR_BATTERY_LEVEL
                    ] = batt[mac]

            # averaging and states updating
            if mac in batt:
                if config[CONF_BATT_ENTITIES]:
                    setattr(sensors[b_i], "_state", batt[mac])
                    try:
                        sensors[b_i].schedule_update_ha_state()
                    except AttributeError:
                        _LOGGER.debug(
                            "Sensor %s (%s, batt.) not yet ready for update",
                            mac,
                            sensortype,
                        )
                    except RuntimeError as err:
                        _LOGGER.error(
                            "Sensor %s (%s, batt.) update error:", mac, sensortype
                        )
                        _LOGGER.error(err)
            if mac in temp_m_data:
                success, error = calc_update_state(
                    sensors[t_i], mac, config, temp_m_data[mac]
                )
                if not success:
                    _LOGGER.error(
                        "Sensor %s (%s, temp.) update error:", mac, sensortype
                    )
                    _LOGGER.error(error)
            if mac in hum_m_data:
                success, error = calc_update_state(
                    sensors[h_i], mac, config, hum_m_data[mac], sensortype
                )
                if not success:
                    _LOGGER.error("Sensor %s (%s, hum.) update error:", mac, sensortype)
                    _LOGGER.error(error)
            if mac in moist_m_data:
                success, error = calc_update_state(
                    sensors[m_i], mac, config, moist_m_data[mac]
                )
                if not success:
                    _LOGGER.error(
                        "Sensor %s (%s, moist.) update error:", mac, sensortype
                    )
                    _LOGGER.error(error)
            if mac in cond_m_data:
                success, error = calc_update_state(
                    sensors[c_i], mac, config, cond_m_data[mac]
                )
                if not success:
                    _LOGGER.error(
                        "Sensor %s (%s, cond.) update error:", mac, sensortype
                    )
                    _LOGGER.error(error)
            if mac in illum_m_data:
                success, error = calc_update_state(
                    sensors[i_i], mac, config, illum_m_data[mac]
                )
                if not success:
                    _LOGGER.error(
                        "Sensor %s (%s, illum.) update error:", mac, sensortype
                    )
                    _LOGGER.error(error)
            if mac in formaldehyde_m_data:
                success, error = calc_update_state(
                    sensors[f_i], mac, config, formaldehyde_m_data[mac], fdec=3
                )
                if not success:
                    _LOGGER.error(
                        "Sensor %s (%s, formaldehyde) update error:", mac, sensortype
                    )
                    _LOGGER.error(error)
            if mac in cons_m_data:
                setattr(sensors[cn_i], "_state", cons_m_data[mac])
                try:
                    sensors[cn_i].schedule_update_ha_state()
                except AttributeError:
                    _LOGGER.debug(
                        "Sensor %s (%s, cons.) not yet ready for update",
                        mac,
                        sensortype,
                    )
                except RuntimeError as err:
                    _LOGGER.error(
                        "Sensor %s (%s, cons.) update error:", mac, sensortype
                    )
                    _LOGGER.error(err)
            if mac in switch_m_data:
                setattr(sensors[sw_i], "_state", switch_m_data[mac])
                try:
                    sensors[sw_i].schedule_update_ha_state()
                except AttributeError:
                    _LOGGER.debug(
                        "Sensor %s (%s, switch) not yet ready for update",
                        mac,
                        sensortype,
                    )
                except RuntimeError as err:
                    _LOGGER.error(
                        "Sensor %s (%s, switch) update error:", mac, sensortype
                    )
                    _LOGGER.error(err)
        _LOGGER.debug(
            "Finished. Parsed: %i hci events, %i xiaomi devices.",
            len(hcidump_raw),
            len(macs),
        )
        return []

    def update_ble(now):
        """Lookup Bluetooth LE devices and update status."""
        period = config[CONF_PERIOD]
        _LOGGER.debug("update_ble called")
        try:
            discover_ble_devices(config)
        except RuntimeError as error:
            _LOGGER.error("Error during Bluetooth LE scan: %s", error)
        track_point_in_utc_time(
            hass, update_ble, dt_util.utcnow() + timedelta(seconds=period)
        )

    update_ble(dt_util.utcnow())
    # Return successful setup
    return True


class TemperatureSensor(Entity):
    """Representation of a sensor."""

    def __init__(self, mac):
        """Initialize the sensor."""
        self._state = None
        self._battery = None
        self._unique_id = "t_" + mac
        self._device_state_attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return "mi {}".format(self._unique_id)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_TEMPERATURE

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
    def force_update(self):
        """Force update."""
        return True


class HumiditySensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, mac):
        """Initialize the sensor."""
        self._state = None
        self._battery = None
        self._unique_id = "h_" + mac
        self._device_state_attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return "mi {}".format(self._unique_id)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_HUMIDITY

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
    def force_update(self):
        """Force update."""
        return True


class MoistureSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, mac):
        """Initialize the sensor."""
        self._state = None
        self._battery = None
        self._unique_id = "m_" + mac
        self._device_state_attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return "mi {}".format(self._unique_id)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_HUMIDITY

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
    def force_update(self):
        """Force update."""
        return True


class ConductivitySensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, mac):
        """Initialize the sensor."""
        self._state = None
        self._battery = None
        self._unique_id = "c_" + mac
        self._device_state_attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return "mi {}".format(self._unique_id)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "µS/cm"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:flash-circle"

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
    def force_update(self):
        """Force update."""
        return True


class IlluminanceSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, mac):
        """Initialize the sensor."""
        self._state = None
        self._battery = None
        self._unique_id = "l_" + mac
        self._device_state_attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return "mi {}".format(self._unique_id)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "lx"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:white-balance-sunny"

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
    def force_update(self):
        """Force update."""
        return True

class FormaldehydeSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, mac):
        """Initialize the sensor."""
        self._state = None
        self._battery = None
        self._unique_id = "f_" + mac
        self._device_state_attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return "mi {}".format(self._unique_id)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "mg/m³"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:chemical-weapon"

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
    def force_update(self):
        """Force update."""
        return True

class BatterySensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, mac):
        """Initialize the sensor."""
        self._state = None
        self._unique_id = "batt_" + mac
        self._device_state_attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return "mi {}".format(self._unique_id)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"

    @property
    def device_class(self):
        """Return the device class."""
        return DEVICE_CLASS_BATTERY

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
    def force_update(self):
        """Force update."""
        return True

class ConsumableSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, mac):
        """Initialize the sensor."""
        self._state = None
        self._battery = None
        self._cn_name = "cn_"
        self._nmac = mac
        self._device_state_attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return "mi {}".format(self._cn_name + self._nmac)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:mdi-recycle-variant"

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
        return self._cn_name + self._nmac

    @property
    def force_update(self):
        """Force update."""
        return True

class SwitchBinarySensor(BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(self, mac):
        """Initialize the sensor."""
        self._state = None
        self._swclass = None
        self._battery = None
        self._unique_id = "sw_" + mac
        self._device_state_attributes = {}

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
