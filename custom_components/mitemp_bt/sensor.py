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
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_TEMPERATURE,
    CONDUCTIVITY,
    PERCENTAGE,
    TEMP_CELSIUS,
    ATTR_BATTERY_LEVEL,
    STATE_OFF, 
    STATE_ON,
)

from homeassistant.components.binary_sensor import BinarySensorEntity
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
    CONF_SENSOR_NAMES,
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

SENSOR_NAMES_LIST_SCHEMA = vol.Schema(
    {
        cv.matches_regex(MAC_REGEX): cv.string
    }
)

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
        vol.Optional(CONF_SENSOR_NAMES, default={}): SENSOR_NAMES_LIST_SCHEMA,
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
                _LOGGER.debug("HCIdump thread: main event_loop stopped, finishing")
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
    adv_index1 = data.find(b"\x02\x01\x06", 14, 17)
    adv_index2 = data.find(b"\x15\x16\x95", 14, 17)
    if adv_index1 == -1 and adv_index2 == -1:
        return None
    elif adv_index1 != -1:
        adv_index = adv_index1
    elif adv_index2 != -1:
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
    #strange positive RSSI workaround
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


def sensor_name(config, mac):
    """Set sensor name."""
    fmac = ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
    if fmac in config[CONF_SENSOR_NAMES]:
        custom_name = config[CONF_SENSOR_NAMES].get(fmac)
        _LOGGER.debug("Name of sensor with mac adress %s is set to: %s", fmac, custom_name)
        return custom_name
    return mac


class BLEScanner:
    """BLE scanner."""

    dumpthreads = []
    hcidump_data = []

    def start(self, config):
        """Start receiving broadcasts."""
        active_scan = config[CONF_ACTIVE_SCAN]
        hci_interfaces = config[CONF_HCI_INTERFACE]
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


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""

    def reverse_mac(rmac):
        """Change LE order to BE."""
        if len(rmac) != 12:
            return None
        return rmac[10:12] + rmac[8:10] + rmac[6:8] + rmac[4:6] + rmac[2:4] + rmac[0:2]

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
    firstrun = True
    scanner = BLEScanner()
    hass.bus.listen("homeassistant_stop", scanner.shutdown_handler)
    scanner.start(config)
    sensors_by_mac = {}
    if config[CONF_REPORT_UNKNOWN]:
        _LOGGER.info(
            "Attention! Option report_unknown is enabled, be ready for a huge output..."
        )
    # prepare device:key list to speedup parser
    aeskeys = {}
    for mac in config[CONF_ENCRYPTORS]:
        p_mac = bytes.fromhex(reverse_mac(mac.replace(":", "")).lower())
        p_key = bytes.fromhex(config[CONF_ENCRYPTORS][mac].lower())
        aeskeys[p_mac] = p_key
    _LOGGER.debug("%s encryptors mac:key pairs loaded.", len(aeskeys))
    whitelist = []
    if isinstance(config[CONF_WHITELIST], bool):
        if config[CONF_WHITELIST] is True:
            for mac in config[CONF_ENCRYPTORS]:
                whitelist.append(mac)
            for mac in config[CONF_SENSOR_NAMES]:
                whitelist.append(mac)
    if isinstance(config[CONF_WHITELIST], list):
        for mac in config[CONF_WHITELIST]:
            whitelist.append(mac)
        for mac in config[CONF_ENCRYPTORS]:
            whitelist.append(mac)
        for mac in config[CONF_SENSOR_NAMES]:
            whitelist.append(mac)
    for i, mac in enumerate(whitelist):
        whitelist[i] = bytes.fromhex(reverse_mac(mac.replace(":", "")).lower())
    _LOGGER.debug("%s whitelist item(s) loaded.", len(whitelist))
    lpacket.cntr = {}
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
        # LYWSD03MMC / MHO-C401 "jagged" humidity workaround
        if stype == "LYWSD03MMC" or stype == "MHO-C401":
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
        except (AttributeError, AssertionError):
            _LOGGER.debug("Sensor %s not yet ready for update", sensor_mac)
            success = True
        except ZeroDivisionError as err:
            error = err
        except IndexError as err:
            error = err
        except RuntimeError as err:
            error = err
        return success, error

    def discover_ble_devices(config, aeskeyslist, whitelist):
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
            _LOGGER.error("HCIdump thread(s) is not completed, interrupting data processing!")
            return []
        hcidump_raw = [*scanner.hcidump_data]
        scanner.start(config)  # minimum delay between HCIdumps
        report_unknown = config[CONF_REPORT_UNKNOWN]
        for msg in hcidump_raw:
            data = parse_raw_message(msg, aeskeyslist, whitelist, report_unknown)
            if data and "mac" in data:
                # ignore duplicated message
                packet = data["packet"]
                prev_packet = lpacket(mac=data["mac"])
                if prev_packet == packet:
                    # _LOGGER.debug("DUPLICATE: %s, IGNORING!", data)
                    continue
                lpacket(data["mac"], packet)
                # store found readings per device
                if "temperature" in data:
                    if CONF_TMAX >= data["temperature"] >= CONF_TMIN:
                        if data["mac"] not in temp_m_data:
                            temp_m_data[data["mac"]] = []
                        temp_m_data[data["mac"]].append(data["temperature"])
                        macs[data["mac"]] = data["mac"]
                    elif log_spikes:
                        _LOGGER.error(
                            "Temperature spike: %s (%s)",
                            data["temperature"],
                            data["mac"],
                        )
                if "humidity" in data:
                    if CONF_HMAX >= data["humidity"] >= CONF_HMIN:
                        if data["mac"] not in hum_m_data:
                            hum_m_data[data["mac"]] = []
                        hum_m_data[data["mac"]].append(data["humidity"])
                        macs[data["mac"]] = data["mac"]
                    elif log_spikes:
                        _LOGGER.error(
                            "Humidity spike: %s (%s)", data["humidity"], data["mac"],
                        )
                if "conductivity" in data:
                    if data["mac"] not in cond_m_data:
                        cond_m_data[data["mac"]] = []
                    cond_m_data[data["mac"]].append(data["conductivity"])
                    macs[data["mac"]] = data["mac"]
                if "moisture" in data:
                    if data["mac"] not in moist_m_data:
                        moist_m_data[data["mac"]] = []
                    moist_m_data[data["mac"]].append(data["moisture"])
                    macs[data["mac"]] = data["mac"]
                if "illuminance" in data:
                    if data["mac"] not in illum_m_data:
                        illum_m_data[data["mac"]] = []
                    illum_m_data[data["mac"]].append(data["illuminance"])
                    macs[data["mac"]] = data["mac"]
                if "formaldehyde" in data:
                    if data["mac"] not in formaldehyde_m_data:
                        formaldehyde_m_data[data["mac"]] = []
                    formaldehyde_m_data[data["mac"]].append(data["formaldehyde"])
                    macs[data["mac"]] = data["mac"]
                if "consumable" in data:
                    cons_m_data[data["mac"]] = int(data["consumable"])
                    macs[data["mac"]] = data["mac"]
                if "switch" in data:
                    switch_m_data[data["mac"]] = int(data["switch"])
                    macs[data["mac"]] = data["mac"]
                if "battery" in data:
                    batt[data["mac"]] = int(data["battery"])
                    macs[data["mac"]] = data["mac"]
                if data["mac"] not in rssi:
                    rssi[data["mac"]] = []
                rssi[data["mac"]].append(int(data["rssi"]))
                stype[data["mac"]] = data["type"]
            else:
                # "empty" loop high cpu usage workaround
                sleep(0.0001)
        # for every seen device
        for mac in macs:
            # fixed entity index for every measurement type
            # according to the sensor implementation
            t_i, h_i, m_i, c_i, i_i, f_i, cn_i, sw_i, b_i = MMTS_DICT[stype[mac]]
            # if necessary, create a list of entities
            # according to the sensor implementation
            if mac in sensors_by_mac:
                sensors = sensors_by_mac[mac]
            else:
                sensors = []
                if t_i != 9:
                    sensors.insert(t_i, TemperatureSensor(config, mac))
                if h_i != 9:
                    sensors.insert(h_i, HumiditySensor(config, mac))
                if m_i != 9:
                    sensors.insert(m_i, MoistureSensor(config, mac))
                if c_i != 9:
                    sensors.insert(c_i, ConductivitySensor(config, mac))
                if i_i != 9:
                    sensors.insert(i_i, IlluminanceSensor(config, mac))
                if f_i != 9:
                    sensors.insert(f_i, FormaldehydeSensor(config, mac))
                if cn_i != 9:
                    sensors.insert(cn_i, ConsumableSensor(config, mac))
                    try:
                        setattr(sensors[cn_i], "_cn_name", CN_NAME_DICT[stype[mac]])
                    except KeyError:
                        pass
                if sw_i != 9:
                    sensors.insert(sw_i, SwitchBinarySensor(config, mac))
                    try:
                        setattr(sensors[sw_i], "_swclass", SW_CLASS_DICT[stype[mac]])
                    except KeyError:
                        pass
                if config[CONF_BATT_ENTITIES] and (b_i != 9):
                    sensors.insert(b_i, BatterySensor(config, mac))
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
                getattr(sensor, "_device_state_attributes")["sensor type"] = stype[mac]
                getattr(sensor, "_device_state_attributes")["mac address"] = (
                    ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
                    )
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
                    except (AttributeError, AssertionError):
                        _LOGGER.debug(
                            "Sensor %s (%s, batt.) not yet ready for update",
                            mac,
                            stype[mac],
                        )
                    except RuntimeError as err:
                        _LOGGER.error(
                            "Sensor %s (%s, batt.) update error:", mac, stype[mac]
                        )
                        _LOGGER.error(err)
            if mac in temp_m_data:
                success, error = calc_update_state(
                    sensors[t_i], mac, config, temp_m_data[mac]
                )
                if not success:
                    _LOGGER.error(
                        "Sensor %s (%s, temp.) update error:", mac, stype[mac]
                    )
                    _LOGGER.error(error)
            if mac in hum_m_data:
                success, error = calc_update_state(
                    sensors[h_i], mac, config, hum_m_data[mac], stype[mac]
                )
                if not success:
                    _LOGGER.error("Sensor %s (%s, hum.) update error:", mac, stype[mac])
                    _LOGGER.error(error)
            if mac in moist_m_data:
                success, error = calc_update_state(
                    sensors[m_i], mac, config, moist_m_data[mac]
                )
                if not success:
                    _LOGGER.error(
                        "Sensor %s (%s, moist.) update error:", mac, stype[mac]
                    )
                    _LOGGER.error(error)
            if mac in cond_m_data:
                success, error = calc_update_state(
                    sensors[c_i], mac, config, cond_m_data[mac]
                )
                if not success:
                    _LOGGER.error(
                        "Sensor %s (%s, cond.) update error:", mac, stype[mac]
                    )
                    _LOGGER.error(error)
            if mac in illum_m_data:
                success, error = calc_update_state(
                    sensors[i_i], mac, config, illum_m_data[mac]
                )
                if not success:
                    _LOGGER.error(
                        "Sensor %s (%s, illum.) update error:", mac, stype[mac]
                    )
                    _LOGGER.error(error)
            if mac in formaldehyde_m_data:
                success, error = calc_update_state(
                    sensors[f_i], mac, config, formaldehyde_m_data[mac], fdec=3
                )
                if not success:
                    _LOGGER.error(
                        "Sensor %s (%s, formaldehyde) update error:", mac, stype[mac]
                    )
                    _LOGGER.error(error)
            if mac in cons_m_data:
                setattr(sensors[cn_i], "_state", cons_m_data[mac])
                try:
                    sensors[cn_i].schedule_update_ha_state()
                except (AttributeError, AssertionError):
                    _LOGGER.debug(
                        "Sensor %s (%s, cons.) not yet ready for update",
                        mac,
                        stype[mac],
                    )
                except RuntimeError as err:
                    _LOGGER.error(
                        "Sensor %s (%s, cons.) update error:", mac, stype[mac]
                    )
                    _LOGGER.error(err)
            if mac in switch_m_data:
                setattr(sensors[sw_i], "_state", switch_m_data[mac])
                try:
                    sensors[sw_i].schedule_update_ha_state()
                except (AttributeError, AssertionError):
                    _LOGGER.debug(
                        "Sensor %s (%s, switch) not yet ready for update",
                        mac,
                        stype[mac],
                    )
                except RuntimeError as err:
                    _LOGGER.error(
                        "Sensor %s (%s, switch) update error:", mac, stype[mac]
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
            discover_ble_devices(config, aeskeys, whitelist)
        except RuntimeError as error:
            _LOGGER.error("Error during Bluetooth LE scan: %s", error)
        track_point_in_utc_time(
            hass, update_ble, dt_util.utcnow() + timedelta(seconds=period)
        )

    update_ble(dt_util.utcnow())
    # Return successful setup
    return True


class MeasuringSensor(Entity):
    """Base class for measuring sensor entity"""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        self._name = ""
        self._state = None
        self._unit_of_measurement = ""
        self._device_class = None
        self._device_state_attributes = {}
        self._unique_id = ""

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def device_class(self):
        """Return the device class."""
        return self._device_class

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

class TemperatureSensor(MeasuringSensor):
    """Representation of a sensor."""

    def __init__(self, config, mac):
        "Initialize the sensor."""
        super().__init__(config, mac)
        self._sensor_name = sensor_name(config, mac)
        self._name = "mi temperature {}".format(self._sensor_name)
        self._unique_id = "t_" + self._sensor_name
        self._unit_of_measurement = TEMP_CELSIUS
        self._device_class = DEVICE_CLASS_TEMPERATURE


class HumiditySensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        super().__init__(config, mac)
        self._sensor_name = sensor_name(config, mac)
        self._name = "mi humidity {}".format(self._sensor_name)
        self._unique_id = "h_" + self._sensor_name
        self._unit_of_measurement = PERCENTAGE 
        self._device_class = DEVICE_CLASS_HUMIDITY


class MoistureSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        super().__init__(config, mac)
        self._sensor_name = sensor_name(config, mac)
        self._name = "mi moisture {}".format(self._sensor_name)
        self._unique_id = "m_" + self._sensor_name
        self._unit_of_measurement = PERCENTAGE 
        self._device_class = DEVICE_CLASS_HUMIDITY


class ConductivitySensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        super().__init__(config, mac)
        self._sensor_name = sensor_name(config, mac)
        self._name = "mi conductivity {}".format(self._sensor_name)
        self._unique_id = "c_" + self._sensor_name
        self._unit_of_measurement = CONDUCTIVITY
        self._device_class = None
        
    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:flash-circle"


class IlluminanceSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        super().__init__(config, mac)
        self._sensor_name = sensor_name(config, mac)
        self._name = "mi llluminance {}".format(self._sensor_name)
        self._unique_id = "l_" + self._sensor_name
        self._unit_of_measurement = "lx"
        self._device_class = DEVICE_CLASS_ILLUMINANCE


class FormaldehydeSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        super().__init__(config, mac)
        self._sensor_name = sensor_name(config, mac)
        self._name = "mi formaldehyde {}".format(self._sensor_name)
        self._unique_id = "f_" + self._sensor_name
        self._unit_of_measurement = "mg/m³"
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:chemical-weapon"


class BatterySensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        super().__init__(config, mac)
        self._sensor_name = sensor_name(config, mac)
        self._name = "mi battery {}".format(self._sensor_name)
        self._unique_id = "batt__" + self._sensor_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = DEVICE_CLASS_BATTERY


class ConsumableSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        super().__init__(config, mac)
        self._sensor_name = sensor_name(config, mac)
        self._name = "mi consumable {}".format(self._sensor_name)
        self._unique_id = "cn__" + self._sensor_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:mdi-recycle-variant"


class SwitchBinarySensor(BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(self, config, mac):
        """Initialize the sensor."""
        self._sensor_name = sensor_name(config, mac)
        self._name = "mi switch {}".format(self._sensor_name)
        self._state = None
        self._unique_id = "sw_" + sensor_name(config, mac)
        self._device_state_attributes = {}
        self._device_class = None

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return bool(self._state)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

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
        """Return the device class."""
        return self._device_class

    @property
    def force_update(self):
        """Force update."""
        return True
