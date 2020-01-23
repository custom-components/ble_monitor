"""Xiaomi Mi BLE monitor integration."""
from datetime import timedelta
import asyncio
from threading import Thread
import logging
#import os
import statistics as sts
import struct
#import subprocess
#import sys
import aioblescan as aiobs
import voluptuous as vol

from homeassistant.const import (
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_HUMIDITY,
    TEMP_CELSIUS,
    ATTR_BATTERY_LEVEL,
)
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
    CONF_ROUNDING,
    CONF_DECIMALS,
    CONF_PERIOD,
    CONF_LOG_SPIKES,
    CONF_USE_MEDIAN,
    CONF_ACTIVE_SCAN,
    CONF_HCI_INTERFACE,
    CONF_TMIN,
    CONF_TMAX,
    CONF_HMIN,
    CONF_HMAX,
    XIAOMI_TYPE_DICT,
    MMTS_DICT
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_ROUNDING, default=DEFAULT_ROUNDING): cv.boolean,
        vol.Optional(CONF_DECIMALS, default=DEFAULT_DECIMALS): cv.positive_int,
        vol.Optional(CONF_PERIOD, default=DEFAULT_PERIOD): cv.positive_int,
        vol.Optional(CONF_LOG_SPIKES, default=DEFAULT_LOG_SPIKES): cv.boolean,
        vol.Optional(CONF_USE_MEDIAN, default=DEFAULT_USE_MEDIAN): cv.boolean,
        vol.Optional(
            CONF_ACTIVE_SCAN, default=DEFAULT_ACTIVE_SCAN
        ): cv.boolean,
        vol.Optional(
            CONF_HCI_INTERFACE, default = DEFAULT_HCI_INTERFACE
        ): cv.positive_int
    }
)

# Structured objects for data conversions
TH_STRUCT = struct.Struct("<hH")
H_STRUCT = struct.Struct("<H")
T_STRUCT = struct.Struct("<h")
CND_STRUCT = struct.Struct("<H")
ILL_STRUCT = struct.Struct("<I")

class HCIdump(Thread):
    """mimic deprecated hcidump tool"""
    def __init__(self, interface = 0, active = 0):
        Thread.__init__(self)
        _LOGGER.debug("HCIdump thread: Init")
        self._interface = interface
        self._active = active
        self._dumplist = []
        self._event_loop = None
        _LOGGER.debug("HCIdump thread: Init finished")

    def process_hci_events(self, data):
        """collect HCI events"""
        self._dumplist.append(data)
    
    def run(self):
        _LOGGER.debug("HCIdump thread: Run")
        self._dumplist = []
        #self._event_loop = asyncio.get_event_loop()
        try:
            mysocket = aiobs.create_bt_socket(self._interface)
        except OSError as error:
            _LOGGER.error("HCIdump thread: OS error: %s", error)
        else:
            self._event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._event_loop)
            fac=self._event_loop._create_connection_transport(# pylint: disable=W0212
                mysocket,aiobs.BLEScanRequester,
                None,
                None
            )
            _LOGGER.debug("HCIdump thread: Connection")
            conn,btctrl = self._event_loop.run_until_complete(fac)
            _LOGGER.debug("HCIdump thread: Connected")
            btctrl.process = self.process_hci_events
            btctrl.send_command(
                aiobs.HCI_Cmd_LE_Set_Scan_Params(
                    scan_type = self._active
                )
            )
            btctrl.send_scan_request()
            _LOGGER.debug("HCIdump thread: start main event_loop")
            self._event_loop.run_forever()
            _LOGGER.debug("HCIdump thread: main event_loop stopped, finishing")
            btctrl.stop_scan_request()
            conn.close()
            self._event_loop.close()
            _LOGGER.debug("HCIdump thread: Run finished")

    def join(self, timeout = 3):
        _LOGGER.debug("HCIdump thread: joining")
        try:
            self._event_loop.call_soon_threadsafe(self._event_loop.stop)
        except AttributeError as error:
            _LOGGER.debug("%s", error)
        Thread.join(self, timeout)
        _LOGGER.debug("HCIdump thread: joined")
        return self._dumplist

def reverse_mac(rmac):
    """Change LE order to BE."""
    if len(rmac) != 12:
        return None
    return (
        rmac[10:12]
        + rmac[8:10]
        + rmac[6:8]
        + rmac[4:6]
        + rmac[2:4]
        + rmac[0:2]
    )


def parse_xiomi_value(hexvalue, typecode):
    """Convert value depending on its type."""
    vlength = len(hexvalue) / 2
    if vlength == 4:
        if typecode == "0D":
            temp, humi = TH_STRUCT.unpack(bytes.fromhex(hexvalue))
            return {"temperature": temp / 10, "humidity": humi / 10}
    if vlength == 2:
        if typecode == "06":
            humi, = H_STRUCT.unpack(bytes.fromhex(hexvalue))
            return {"humidity": humi / 10}
        if typecode == "04":
            temp, = T_STRUCT.unpack(bytes.fromhex(hexvalue))
            return {"temperature": temp / 10}
        if typecode == "09":
            cond, = CND_STRUCT.unpack(bytes.fromhex(hexvalue))
            return {"conductivity": cond}
    if vlength == 1:
        if typecode == "0A":
            return {"battery": int(hexvalue, 16)}
        if typecode == "08":
            return {"moisture": int(hexvalue, 16)}
    if vlength == 3:
        if typecode == "07":
            illum, = ILL_STRUCT.unpack(bytes.fromhex(hexvalue + "00"))
            return {"illuminance": illum}
    return {}


def parse_raw_message(data):
    """Parse the raw data."""
    if data is None:
        return None

    # check for Xiaomi service data
    xiaomi_index = data.find("1695FE", 33)
    if xiaomi_index == -1:
        return None

    # check for no BR/EDR + LE General discoverable mode flags
    adv_index = data.find("020106", 28, 34)
    if adv_index == -1:
        return None

    # check for BTLE msg size
    msg_length = int(data[4:6], 16) * 2 + 6
    if msg_length != len(data):
        return None

    # check for MAC presence in message and in service data
    xiaomi_mac_reversed = data[xiaomi_index + 16:xiaomi_index + 28]
    source_mac_reversed = data[adv_index - 14:adv_index - 2]
    if xiaomi_mac_reversed != source_mac_reversed:
        return None

    # check if RSSI is valid
    rssi, = struct.unpack(
        "<b", bytes.fromhex(data[msg_length - 2:msg_length])
    )
    if not 0 >= rssi >= -127:
        return None

    try:
        sensor_type, toffset = XIAOMI_TYPE_DICT[
            data[xiaomi_index + 8:xiaomi_index + 14]
        ]
    except KeyError:
        _LOGGER.debug(
            "Unknown sensor type: %s",
            data[xiaomi_index + 8:xiaomi_index + 14],
        )
        return None

    # xiaomi data length = message length
    #     -all bytes before XiaomiUUID
    #     -3 bytes Xiaomi UUID + ADtype
    #     -1 byte rssi
    #     -3+1 bytes sensor type
    #     -1 byte packet_id
    #     -6 bytes MAC
    #     - sensortype offset
    xdata_length = msg_length - xiaomi_index - 30 - toffset * 2
    if xdata_length < 8:
        return None
    xdata_point = xiaomi_index + (14 + toffset) * 2
    xnext_point = xdata_point + 6
    # check if xiaomi data start and length is valid
    if xdata_length != len(data[xdata_point:-2]):
        return None

    packet_id = int(data[xiaomi_index + 14:xiaomi_index + 16], 16)
    result = {
        "rssi": rssi,
        "mac": reverse_mac(xiaomi_mac_reversed),
        "type": sensor_type,
        "packet": packet_id,
    }

    # loop through xiaomi payload
    # assume that the data may have several values ​​of different types,
    # although I did not notice this behavior with my LYWSDCGQ sensors
    while True:
        xvalue_typecode = data[xdata_point:xdata_point + 2]
        try:
            xvalue_length = int(data[xdata_point + 4:xdata_point + 6], 16)
        except ValueError as error:
            _LOGGER.error("xvalue_length conv. error: %s", error)
            result = {}
            break
        xnext_point = xdata_point + 6 + xvalue_length * 2
        xvalue = data[xdata_point + 6:xnext_point]
        res = parse_xiomi_value(xvalue, xvalue_typecode)
        if res:
            result.update(res)
        if xnext_point > msg_length - 6:
            break
        xdata_point = xnext_point
    return result


class BLEScanner:
    """BLE scanner."""

    #hcitool = None
    #hcidump = None
    #tempf = tempfile.TemporaryFile(mode="w+b")
    #devnull = (
    #    subprocess.DEVNULL
    #    if sys.version_info > (3, 0)
    #    else open(os.devnull, "wb")
    #)
    dumpthread = None

    def start(self, config):
        """Start receiving broadcasts."""
        active_scan = config[CONF_ACTIVE_SCAN]
        hci_interface = config[CONF_HCI_INTERFACE]
        #hcitoolcmd = ["hcitool", "lescan", "--duplicates", "--passive"]
        _LOGGER.debug("Spawning HCIdump thread.")
        self.dumpthread = HCIdump(
            interface = hci_interface,
            active = int(active_scan is True)
        )
        #self.dumpthread.daemon = True
        _LOGGER.debug("Starting HCIdump thread.")
        self.dumpthread.start()
        #if active_scan:
        #    hcitoolcmd = ["hcitool", "lescan", "--duplicates"]
        #self.hcitool = subprocess.Popen(
        #    hcitoolcmd, stdout=self.devnull, stderr=self.devnull
        #)
        #self.hcidump = subprocess.Popen(
        #   ["hcidump", "--raw", "hci"], stdout=self.tempf, stderr=self.devnull
        #)

    #def stop(self):
    #    """Stop receiving broadcasts."""
    #    _LOGGER.debug("Stop receiving broadcasts")
        #self.hcidump.terminate()
        #self.hcidump.communicate()
        #self.hcitool.terminate()
        #self.hcitool.communicate()

    def shutdown_handler(self, event):
        """Run homeassistant_stop event handler."""
        _LOGGER.debug("Running homeassistant_stop event handler: %s", event)
        self.dumpthread.join()
        #self.hcidump.kill()
        #self.hcidump.communicate()
        #self.hcitool.kill()
        #self.hcitool.communicate()
        #self.tempf.close()

    #def messages(self):
    #    """Get data from hcidump."""
    #    data = ""
    #    try:
    #        _LOGGER.debug("reading hcidump...")
    #        self.tempf.flush()
    #        self.tempf.seek(0)
    #        for line in self.tempf:
    #            try:
    #                sline = line.decode()
    #            except AttributeError:
    #                _LOGGER.debug("Error decoding line: %s", line)
    #            # _LOGGER.debug(line)
    #            if sline.startswith("> "):
    #                yield data
    #                data = sline[2:].strip().replace(" ", "")
    #            elif sline.startswith("< "):
    #                yield data
    #                data = ""
    #            else:
    #                data += sline.strip().replace(" ", "")
    #    except RuntimeError as error:
    #        _LOGGER.error("Error during reading of hcidump: %s", error)
    #        data = ""
    #    self.tempf.seek(0)
    #    self.tempf.truncate(0)
    #    yield data


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    _LOGGER.debug("Starting")
    scanner = BLEScanner()
    hass.bus.listen("homeassistant_stop", scanner.shutdown_handler)
    scanner.start(config)

    sensors_by_mac = {}

    def discover_ble_devices(config):
        """Discover Bluetooth LE devices."""
        #_LOGGER.debug("Discovering Bluetooth LE devices")
        rounding = config[CONF_ROUNDING]
        decimals = config[CONF_DECIMALS]
        log_spikes = config[CONF_LOG_SPIKES]
        use_median = config[CONF_USE_MEDIAN]

        #_LOGGER.debug("Stopping")
        #scanner.stop()

        _LOGGER.debug("Time to analyze...")
        stype = {}
        hum_m_data = {}
        temp_m_data = {}
        illum_m_data = {}
        moist_m_data = {}
        cond_m_data = {}
        batt = {}  # battery
        lpacket = {}  # last packet number
        rssi = {}
        macs = {}  # all found macs
        _LOGGER.debug("Getting data from HCIdump thread")
        for msg in scanner.dumpthread.join():
            data = parse_raw_message(''.join('{:02X}'.format(x) for x in msg))
            if data and "mac" in data:
                # ignore duplicated message
                packet = int(data["packet"])
                if data["mac"] in lpacket:
                    prev_packet = lpacket[data["mac"]]
                else:
                    prev_packet = None
                if prev_packet == packet:
                    _LOGGER.debug("DUPLICATE: %s, IGNORING!", data)
                    continue
                _LOGGER.debug("NEW DATA: %s", data)
                lpacket[data["mac"]] = packet
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
                            "Humidity spike: %s (%s)",
                            data["humidity"],
                            data["mac"],
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
                if "battery" in data:
                    batt[data["mac"]] = int(data["battery"])
                    macs[data["mac"]] = data["mac"]
                if data["mac"] not in rssi:
                    rssi[data["mac"]] = []
                rssi[data["mac"]].append(int(data["rssi"]))
                stype[data["mac"]] = data["type"]

        # for every seen device
        for mac in macs:
            # fixed sensor index for every measurement type
            t_i, h_i, m_i, c_i, i_i = MMTS_DICT[stype[mac]]
            if mac in sensors_by_mac:
                sensors = sensors_by_mac[mac]
            else:
                try:
                    if stype[mac] == "HHCCJCY01":
                        sensors = [None] * 4
                        sensors[t_i] = TemperatureSensor(mac)
                        sensors[m_i] = MoistureSensor(mac)
                        sensors[c_i] = ConductivitySensor(mac)
                        sensors[i_i] = IlluminanceSensor(mac)
                    elif stype[mac] == "HHCCPOT002":
                        sensors = [None] * 2
                        sensors[m_i] = MoistureSensor(mac)
                        sensors[c_i] = ConductivitySensor(mac)
                    else:
                        sensors = [None] * 2
                        sensors[t_i] = TemperatureSensor(mac)
                        sensors[h_i] = HumiditySensor(mac)
                except IndexError as error:
                    _LOGGER.error(
                        "Sensor implementation error for %s, %s!",
                        stype[mac],
                        mac
                    )
                    _LOGGER.error(error)
                    continue
                sensors_by_mac[mac] = sensors
                add_entities(sensors)
            for sensor in sensors:
                getattr(sensor, "_device_state_attributes")[
                    "last packet id"
                ] = lpacket[mac]
                getattr(sensor, "_device_state_attributes")[
                    "rssi"
                ] = round(sts.mean(rssi[mac]))
                getattr(sensor, "_device_state_attributes")[
                    "sensor type"
                ] = stype[mac]
                if mac in batt:
                    getattr(sensor, "_device_state_attributes")[
                        ATTR_BATTERY_LEVEL
                    ] = batt[mac]
            # averaging and states updating
            tempstate_mean = None
            humstate_mean = None
            illumstate_mean = None
            moiststate_mean = None
            condstate_mean = None
            tempstate_median = None
            humstate_median = None
            illumstate_median = None
            moiststate_median = None
            condstate_median = None
            if use_median:
                textattr = "last median of"
            else:
                textattr = "last mean of"
            if mac in temp_m_data:
                try:
                    if rounding:
                        tempstate_median = round(
                            sts.median(temp_m_data[mac]), decimals
                        )
                        tempstate_mean = round(
                            sts.mean(temp_m_data[mac]), decimals
                        )
                    else:
                        tempstate_median = sts.median(temp_m_data[mac])
                        tempstate_mean = sts.mean(temp_m_data[mac])
                    if use_median:
                        setattr(sensors[t_i], "_state", tempstate_median)
                    else:
                        setattr(sensors[t_i], "_state", tempstate_mean)
                    getattr(sensors[t_i], "_device_state_attributes")[
                        textattr
                    ] = len(temp_m_data[mac])
                    getattr(sensors[t_i], "_device_state_attributes")[
                        "median"
                    ] = tempstate_median
                    getattr(sensors[t_i], "_device_state_attributes")[
                        "mean"
                    ] = tempstate_mean
                    sensors[t_i].async_schedule_update_ha_state()
                except AttributeError:
                    _LOGGER.info("Sensor %s not yet ready for update", mac)
                except ZeroDivisionError:
                    _LOGGER.error(
                        "Division by zero while temperature averaging!"
                    )
                    continue
                except IndexError as error:
                    _LOGGER.error(
                        "Sensor %s (%s, temp.) update error:", mac, stype[mac]
                    )
                    _LOGGER.error("%s. Index is %i!", error, t_i)
            if mac in hum_m_data:
                try:
                    if rounding:
                        humstate_median = round(
                            sts.median(hum_m_data[mac]), decimals
                        )
                        humstate_mean = round(
                            sts.mean(hum_m_data[mac]), decimals
                        )
                    else:
                        humstate_median = sts.median(hum_m_data[mac])
                        humstate_mean = sts.mean(hum_m_data[mac])
                    if use_median:
                        setattr(sensors[h_i], "_state", humstate_median)
                    else:
                        setattr(sensors[h_i], "_state", humstate_mean)
                    getattr(sensors[h_i], "_device_state_attributes")[
                        textattr
                    ] = len(hum_m_data[mac])
                    getattr(sensors[h_i], "_device_state_attributes")[
                        "median"
                    ] = humstate_median
                    getattr(sensors[h_i], "_device_state_attributes")[
                        "mean"
                    ] = humstate_mean
                    sensors[h_i].async_schedule_update_ha_state()
                except AttributeError:
                    _LOGGER.info("Sensor %s not yet ready for update", mac)
                except ZeroDivisionError:
                    _LOGGER.error("Division by zero while humidity averaging!")
                    continue
                except IndexError as error:
                    _LOGGER.error(
                        "Sensor %s (%s, hum.) update error:", mac, stype[mac]
                    )
                    _LOGGER.error("%s. Index is %i!", error, h_i)
            if mac in moist_m_data:
                try:
                    if rounding:
                        moiststate_median = round(
                            sts.median(moist_m_data[mac]), decimals
                        )
                        moiststate_mean = round(
                            sts.mean(moist_m_data[mac]), decimals
                        )
                    else:
                        moiststate_median = sts.median(moist_m_data[mac])
                        moiststate_mean = sts.mean(moist_m_data[mac])
                    if use_median:
                        setattr(sensors[m_i], "_state", moiststate_median)
                    else:
                        setattr(sensors[m_i], "_state", moiststate_mean)
                    getattr(sensors[m_i], "_device_state_attributes")[
                        textattr
                    ] = len(moist_m_data[mac])
                    getattr(sensors[m_i], "_device_state_attributes")[
                        "median"
                    ] = moiststate_median
                    getattr(sensors[m_i], "_device_state_attributes")[
                        "mean"
                    ] = moiststate_mean
                    sensors[m_i].async_schedule_update_ha_state()
                except AttributeError:
                    _LOGGER.info("Sensor %s not yet ready for update", mac)
                except ZeroDivisionError:
                    _LOGGER.error("Division by zero while moisture averaging!")
                    continue
                except IndexError as error:
                    _LOGGER.error(
                        "Sensor %s (%s, moist.) update error:", mac, stype[mac]
                    )
                    _LOGGER.error("%s. Index is %i!", error, m_i)
            if mac in cond_m_data:
                try:
                    if rounding:
                        condstate_median = round(
                            sts.median(cond_m_data[mac]), decimals
                        )
                        condstate_mean = round(
                            sts.mean(cond_m_data[mac]), decimals
                        )
                    else:
                        condstate_median = sts.median(cond_m_data[mac])
                        condstate_mean = sts.mean(cond_m_data[mac])
                    if use_median:
                        setattr(sensors[c_i], "_state", condstate_median)
                    else:
                        setattr(sensors[c_i], "_state", condstate_mean)
                    getattr(sensors[c_i], "_device_state_attributes")[
                        textattr
                    ] = len(cond_m_data[mac])
                    getattr(sensors[c_i], "_device_state_attributes")[
                        "median"
                    ] = condstate_median
                    getattr(sensors[c_i], "_device_state_attributes")[
                        "mean"
                    ] = condstate_mean
                    sensors[c_i].async_schedule_update_ha_state()
                except AttributeError:
                    _LOGGER.info("Sensor %s not yet ready for update", mac)
                except ZeroDivisionError:
                    _LOGGER.error("Division by zero while humidity averaging!")
                    continue
                except IndexError as error:
                    _LOGGER.error(
                        "Sensor %s (%s, cond.) update error:", mac, stype[mac]
                    )
                    _LOGGER.error("%s. Index is %i!", error, c_i)
            if mac in illum_m_data:
                try:
                    if rounding:
                        illumstate_median = round(
                            sts.median(illum_m_data[mac]), decimals
                        )
                        illumstate_mean = round(
                            sts.mean(illum_m_data[mac]), decimals
                        )
                    else:
                        illumstate_median = sts.median(illum_m_data[mac])
                        illumstate_mean = sts.mean(illum_m_data[mac])
                    if use_median:
                        setattr(sensors[i_i], "_state", illumstate_median)
                    else:
                        setattr(sensors[i_i], "_state", illumstate_mean)
                    getattr(sensors[i_i], "_device_state_attributes")[
                        textattr
                    ] = len(illum_m_data[mac])
                    getattr(sensors[i_i], "_device_state_attributes")[
                        "median"
                    ] = illumstate_median
                    getattr(sensors[i_i], "_device_state_attributes")[
                        "mean"
                    ] = illumstate_mean
                    sensors[i_i].async_schedule_update_ha_state()
                except AttributeError:
                    _LOGGER.info("Sensor %s not yet ready for update", mac)
                except ZeroDivisionError:
                    _LOGGER.error(
                        "Division by zero while illuminance averaging!"
                    )
                    continue
                except IndexError as error:
                    _LOGGER.error(
                        "Sensor %s (%s, illum.) update error:", mac, stype[mac]
                    )
                    _LOGGER.error("%s. Index is %i!", error, i_i)
        scanner.start(config)
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
        """Return the unit of measurement."""
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
        """Return the unit of measurement."""
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
        """Return the unit of measurement."""
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
