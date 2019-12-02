"""Xiaomi Mi temperature and humidity monitor integration."""
from datetime import timedelta
import logging
import os
import statistics
import struct
import subprocess
import sys
import tempfile
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
    DEFAULT_HCITOOL_ACTIVE,
    CONF_ROUNDING,
    CONF_DECIMALS,
    CONF_PERIOD,
    CONF_LOG_SPIKES,
    CONF_USE_MEDIAN,
    CONF_HCITOOL_ACTIVE,
    CONF_TMIN,
    CONF_TMAX,
    CONF_HMIN,
    CONF_HMAX,
    XIAOMI_TYPE_DICT
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
            CONF_HCITOOL_ACTIVE, default=DEFAULT_HCITOOL_ACTIVE
        ): cv.boolean,
    }
)

# Structured objects for data conversions
TH_STRUCT  = struct.Struct('<hH')
H_STRUCT   = struct.Struct('<H')
T_STRUCT   = struct.Struct('<h')
CND_STRUCT = struct.Struct('<H')
ILL_STRUCT = struct.Struct('<I')

def reverse_mac(rmac):
    """change LE order to BE"""
    if len(rmac)!=12:
        return None
    return (rmac[10:12]
        + rmac[8:10]
        + rmac[6:8]
        + rmac[4:6]
        + rmac[2:4]
        + rmac[0:2])

def parse_xiomi_value(hexvalue, typecode):
    """converts a value depending on its type"""
    vlength = len(hexvalue)/2
    if vlength == 4:
        if typecode == "0D":
            temp, humi = TH_STRUCT.unpack(bytes.fromhex(hexvalue))
            return {
                "temperature" : temp/10,
                "humidity" : humi/10
            }
    if vlength == 2:
        if typecode == "06":
            humi, = H_STRUCT.unpack(bytes.fromhex(hexvalue))
            return {
                "humidity" : humi / 10
            }
        if typecode == "04":
            temp, = T_STRUCT.unpack(bytes.fromhex(hexvalue))
            return {
                "temperature" : temp / 10
            }
        if typecode == "09":
            cond, = CND_STRUCT.unpack(bytes.fromhex(hexvalue))
            return {
                "conductivity" : cond
            }
    if vlength == 1:
        if typecode == "0A":
            return {
                "battery" : int(hexvalue, 16)
            }
        if typecode == "08":
            return {
                "moisture" : int(hexvalue, 16)
            }
    if vlength == 3:
        if typecode == "07":
            illum, = ILL_STRUCT.unpack(bytes.fromhex(hexvalue + "00"))
            return {
                "illuminance" : illum
            }
    return {}

def parse_raw_message(data):
    """Parse the raw data."""
    if data is None:
        return None

    # check for Xiaomi? service data
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

    #check for MAC presence in msg and in service data
    xiaomi_mac_reversed = data[xiaomi_index + 16:xiaomi_index + 28]
    source_mac_reversed = data[adv_index - 14:adv_index - 2]
    if xiaomi_mac_reversed != source_mac_reversed:
        return None

    try:
        sensor_type, toffset = (
            XIAOMI_TYPE_DICT[data[xiaomi_index + 8:xiaomi_index + 14]]
        )
    except KeyError:
        _LOGGER.debug(
            "Unknown sensor type: %s",
            data[xiaomi_index + 8:xiaomi_index + 14]
        )
        return None

    # xiaomi data length = message length
    #                    -all bytes before XiaomiUUID
    #                    -1 byte rssi
    #                    -3 bytes sensor type -1 byte
    #                    -1 byte packet_id
    #                    -6 bytes MAC
    #                    - sensortype offset
    xdata_length = (msg_length - xiaomi_index - (12 + toffset) * 2) / 2
    if xdata_length < 4:
        return None

    rssi, = struct.unpack('<b', bytes.fromhex(
        data[msg_length-2:msg_length]
    ))
    xdata_point = xiaomi_index + (14 + toffset) * 2
    packet_id = int(data[xiaomi_index + 14:xiaomi_index + 16], 16)
    result = {
        "rssi" : rssi,
        "mac" : reverse_mac(xiaomi_mac_reversed),
        "type" : sensor_type,
        "packet" : packet_id
    }

    # loop through xiaomi payload
    # assume that the data may have several values ​​of different types,
    # although I did not notice this behavior with my LYWSDCGQ sensors
    while True:
        xvalue_typecode = data[xdata_point:xdata_point+2]
        xvalue_length = int(data[xdata_point+4:xdata_point+6], 16)
        xnext_point = xdata_point + 6 + xvalue_length * 2
        xvalue = (
            data[xdata_point + 6:xnext_point]
        )
        result.update(parse_xiomi_value(xvalue, xvalue_typecode))
        if xnext_point >= msg_length - 2:
            break
        xdata_point = xnext_point
    return result

class BLEScanner:
    """BLE scanner."""

    hcitool = None
    hcidump = None
    tempf = tempfile.SpooledTemporaryFile()

    def start(self, config):
        """Start receiving broadcasts."""
        hcitool_active = config[CONF_HCITOOL_ACTIVE]
        _LOGGER.debug("Temp dir used: %s", tempfile.gettempdir())
        _LOGGER.debug("Start receiving broadcasts")
        devnull = (
            subprocess.DEVNULL
            if sys.version_info > (3, 0)
            else open(os.devnull, "wb")
        )
        hcitoolcmd = ["hcitool", "lescan", "--duplicates", "--passive"]
        if hcitool_active:
            hcitoolcmd = ["hcitool", "lescan", "--duplicates"]
        self.hcitool = subprocess.Popen(
            hcitoolcmd, stdout=devnull, stderr=devnull
        )
        self.hcidump = subprocess.Popen(
            ["hcidump", "--raw", "hci"], stdout=self.tempf, stderr=None
        )

    def stop(self):
        """Stop receiving broadcasts."""
        _LOGGER.debug("Stop receiving broadcasts")
        self.hcitool.kill()
        self.hcidump.kill()

    def messages(self):
        """Get data from hcidump."""
        data = ""
        try:
            _LOGGER.debug("reading hcidump...")
            self.tempf.flush()
            self.tempf.seek(0)
            for line in self.tempf:
                try: line = line.decode()
                except AttributeError: pass
                # _LOGGER.debug(line)
                if line.startswith("> "):
                    yield data
                    data = line[2:].strip().replace(" ", "")
                elif line.startswith("< "):
                    yield data
                    data = ""
                else:
                    data += line.strip().replace(" ", "")
            self.tempf.seek(0)
            self.tempf.truncate(0)
        except RuntimeError as error:
            _LOGGER.error("Error during reading of hcidump: %s", error)
            data = ""
        yield data

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    _LOGGER.debug("Starting")
    scanner = BLEScanner()
    scanner.start(config)

    sensors_by_mac = {}

    def discover_ble_devices(config):
        """Discover Bluetooth LE devices."""
        _LOGGER.debug("Discovering Bluetooth LE devices")
        rounding = config[CONF_ROUNDING]
        decimals = config[CONF_DECIMALS]
        log_spikes = config[CONF_LOG_SPIKES]
        use_median = config[CONF_USE_MEDIAN]

        _LOGGER.debug("Stopping")
        scanner.stop()

        _LOGGER.debug("Analyzing")
        stype = {}
        hum_m_data = {}
        temp_m_data = {}
        batt = {}  # battery
        lpacket = {}  # last packet number
        rssi = {}
        macs = {}  # all found macs
        for msg in scanner.messages():
            data = parse_raw_message(msg)
            if data and "mac" in data:
                _LOGGER.debug("Parsed: %s", data)

                # store found readings per device
                if "temperature" in data:
                    if CONF_TMAX >= data["temperature"] >= CONF_TMIN:
                        if data["mac"] not in temp_m_data:
                            temp_m_data[data["mac"]] = []
                        temp_m_data[data["mac"]].append(data["temperature"])
                        macs[data["mac"]] = data["mac"]
                    elif log_spikes:
                        _LOGGER.error(
                            "Temperature spike: %s (%s)", data["temperature"],
                                                          data["mac"]
                        )
                if "humidity" in data:
                    if CONF_HMAX >= data["humidity"] >= CONF_HMIN:
                        if data["mac"] not in hum_m_data:
                            hum_m_data[data["mac"]] = []
                        hum_m_data[data["mac"]].append(data["humidity"])
                        macs[data["mac"]] = data["mac"]
                    elif log_spikes:
                        _LOGGER.error(
                            "Humidity spike: %s (%s)", data["humidity"],
                                                       data["mac"]
                        )
                if "battery" in data:
                    batt[data["mac"]] = int(data["battery"])
                    macs[data["mac"]] = data["mac"]
                if data["mac"] not in rssi:
                            rssi[data["mac"]] = []
                rssi[data["mac"]].append(int(data["rssi"]))

                lpacket[data["mac"]] = int(data["packet"])
                stype[data["mac"]] = data["type"]

        # for every seen device
        for mac in macs:
            if mac in sensors_by_mac:
                sensors = sensors_by_mac[mac]
            else:
                if stype[mac] == "HHCCJCY01":
                    sensors = [TemperatureSensor(mac)]
                else:
                    sensors = [TemperatureSensor(mac), HumiditySensor(mac)]
                sensors_by_mac[mac] = sensors
                add_entities(sensors)
            for sensor in sensors:
                getattr(sensor, "_device_state_attributes")[
                    "last packet id"] = lpacket[mac]
                getattr(sensor, "_device_state_attributes")[
                    "rssi"] = round(statistics.mean(rssi[mac]))
                getattr(sensor, "_device_state_attributes")[
                    "sensor type"] = stype[mac]
            if mac in batt:
                getattr(sensors[0], "_device_state_attributes")[
                    ATTR_BATTERY_LEVEL
                ] = batt[mac]
                getattr(sensors[1], "_device_state_attributes")[
                    ATTR_BATTERY_LEVEL
                ] = batt[mac]
            # averaging and states updating
            tempstate_mean = None
            humstate_mean = None
            tempstate_median = None
            humstate_median = None
            if use_median:
                textattr = "last median of"
            else:
                textattr = "last mean of"
            if mac in temp_m_data:
                try:
                    if rounding:
                        tempstate_median = round(
                            statistics.median(temp_m_data[mac]), decimals
                        )
                        tempstate_mean = round(
                            statistics.mean(temp_m_data[mac]), decimals
                        )
                    else:
                        tempstate_median = statistics.median(temp_m_data[mac])
                        tempstate_mean = statistics.mean(temp_m_data[mac])
                    if use_median:
                        setattr(sensors[0], "_state", tempstate_median)
                    else:
                        setattr(sensors[0], "_state", tempstate_mean)
                    getattr(sensors[0], "_device_state_attributes")[
                        textattr
                    ] = len(temp_m_data[mac])
                    getattr(sensors[0], "_device_state_attributes")[
                        "median"
                    ] = tempstate_median
                    getattr(sensors[0], "_device_state_attributes")[
                        "mean"
                    ] = tempstate_mean
                    sensors[0].async_schedule_update_ha_state()
                except AttributeError:
                    _LOGGER.info("Sensor %s not yet ready for update", mac)
                except ZeroDivisionError:
                    _LOGGER.error(
                        "Division by zero while temperature averaging!"
                    )
                    continue
            if mac in hum_m_data:
                try:
                    if rounding:
                        humstate_median = round(
                            statistics.median(hum_m_data[mac]), decimals
                        )
                        humstate_mean = round(
                            statistics.mean(hum_m_data[mac]), decimals
                        )
                    else:
                        humstate_median = statistics.median(hum_m_data[mac])
                        humstate_mean = statistics.mean(hum_m_data[mac])
                    if use_median:
                        setattr(sensors[1], "_state", humstate_median)
                    else:
                        setattr(sensors[1], "_state", humstate_mean)
                    getattr(sensors[1], "_device_state_attributes")[
                        textattr
                    ] = len(hum_m_data[mac])
                    getattr(sensors[1], "_device_state_attributes")[
                        "median"
                    ] = humstate_median
                    getattr(sensors[1], "_device_state_attributes")[
                        "mean"
                    ] = humstate_mean
                    sensors[1].async_schedule_update_ha_state()
                except AttributeError:
                    _LOGGER.info("Sensor %s not yet ready for update", mac)
                except ZeroDivisionError:
                    _LOGGER.error("Division by zero while humidity averaging!")
                    continue
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
    """Representation of a Sensor."""

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
