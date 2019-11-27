"""Xiaomi Mi temperature and humidity monitor integration."""
from datetime import timedelta
import logging
import os
import statistics
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


def parse_raw_data(data):
    """Parse the raw data."""
    if not data:
        return None

    result = {}

    adv_index = data.find("020106")

    if adv_index == -1:
        return None

    payload_length = (len(data) - adv_index - 18 * 2) / 2
    if payload_length < 4:
        return None

    mac_reversed = data[adv_index + 24:adv_index + 36]
    source_mac_reversed = data[adv_index - 14:adv_index - 2]

    if mac_reversed != source_mac_reversed:
        return None

    mac = (
        mac_reversed[10:12]
        + mac_reversed[8:10]
        + mac_reversed[6:8]
        + mac_reversed[4:6]
        + mac_reversed[2:4]
        + mac_reversed[0:2]
    )

    packet_id = int(data[adv_index + 22:adv_index + 24], 16)
    type_start = adv_index + 36
    type_code = data[type_start:type_start + 2]
    length = data[type_start + 4:type_start + 6]

    if type_code == "0D" and length == "04" and payload_length in (8, 12):
        temperature_hex = data[type_start + 6:type_start + 10]
        humidity_hex = data[type_start + 10:type_start + 14]
        temperature_dec = int(
            "".join(temperature_hex[2:4] + temperature_hex[0:2]), 16
        )
        temperature = (
            -(temperature_dec & 0x8000) | (temperature_dec & 0x7FFF)
        ) / 10
        humidity = (
            (int(humidity_hex[2:4], 16) << 8) + int(humidity_hex[0:2], 16)
        ) / 10
        result = {
            "temperature": temperature,
            "humidity": humidity,
            "mac": mac,
            "packet": packet_id,
        }
        if payload_length == 12:
            result["battery"] = int(
                data[type_start + 20:type_start + 22], 16
            )
    if type_code == "04" and length == "02" and payload_length in (6, 10):
        temperature_hex = data[type_start + 6:type_start + 10]
        temperature_dec = int(
            "".join(temperature_hex[2:4] + temperature_hex[0:2]), 16
        )
        temperature = (
            -(temperature_dec & 0x8000) | (temperature_dec & 0x7FFF)
        ) / 10
        result = {"temperature": temperature, "mac": mac, "packet": packet_id}
        if payload_length == 10:
            result["battery"] = int(
                data[type_start + 16:type_start + 18], 16
            )
    if type_code == "06" and length == "02" and payload_length in (6, 10):
        humidity_hex = data[type_start + 6:type_start + 10]
        humidity = (
            (int(humidity_hex[2:4], 16) << 8) + int(humidity_hex[0:2], 16)
        ) / 10
        result = {"humidity": humidity, "mac": mac, "packet": packet_id}
        if payload_length == 10:
            result["battery"] = int(
                data[type_start + 16:type_start + 18], 16
            )
    if type_code == "0A" and length == "01" and payload_length == 5:
        battery = int(data[type_start + 6:type_start + 8], 16)
        result = {"battery": battery, "mac": mac, "packet": packet_id}

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

    def get_lines(self):
        """Get data from hcidump."""
        data = None
        try:
            _LOGGER.debug("reading hcidump...")
            self.tempf.flush()
            self.tempf.seek(0)
            for line in self.tempf:
                line = line.decode()
                # _LOGGER.debug(line)
                if line.startswith("> "):
                    yield data
                    data = line[2:].strip().replace(" ", "")
                elif line.startswith("< "):
                    data = None
                else:
                    if data:
                        data += line.strip().replace(" ", "")
            self.tempf.seek(0)
            self.tempf.truncate(0)
        except RuntimeError as error:
            _LOGGER.error("Error during reading of hcidump: %s", error)
            data = []
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
        hum_m_data = {}
        temp_m_data = {}
        batt = {}  # battery
        lpacket = {}  # last packet number
        macs = {}  # all found macs
        for line in scanner.get_lines():
            data = parse_raw_data(line)
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
                lpacket[data["mac"]] = int(data["packet"])

        # for every seen device
        for mac in macs:
            if mac in sensors_by_mac:
                sensors = sensors_by_mac[mac]
            else:
                sensors = [TemperatureSensor(mac), HumiditySensor(mac)]
                sensors_by_mac[mac] = sensors
                add_entities(sensors)
            getattr(sensors[0], "_device_state_attributes")[
                "last packet id"
            ] = lpacket[mac]
            getattr(sensors[1], "_device_state_attributes")[
                "last packet id"
            ] = lpacket[mac]
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
