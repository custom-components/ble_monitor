"""Passive BLE monitor sensor platform."""
from datetime import timedelta
import asyncio
import logging
import statistics as sts

from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_VOLTAGE,
    CONDUCTIVITY,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    VOLT,
    ATTR_BATTERY_LEVEL,
    CONF_DEVICES,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    CONF_UNIQUE_ID,
)

try:
    from homeassistant.const import PERCENTAGE
except ImportError:
    from homeassistant.const import UNIT_PERCENTAGE as PERCENTAGE

from homeassistant.helpers.restore_state import RestoreEntity
import homeassistant.util.dt as dt_util

from .const import (
    CONF_ROUNDING,
    CONF_DECIMALS,
    CONF_PERIOD,
    CONF_LOG_SPIKES,
    CONF_USE_MEDIAN,
    CONF_BATT_ENTITIES,
    CONF_RESTORE_STATE,
    CONF_TMIN,
    CONF_TMAX,
    CONF_HMIN,
    CONF_HMAX,
    KETTLES,
    MANUFACTURER_DICT,
    MMTS_DICT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, conf, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    return True


async def async_setup_entry(hass, config_entry, add_entities):
    """Set up the measuring sensor entry."""
    _LOGGER.debug("Starting measuring sensor entry startup")

    blemonitor = hass.data[DOMAIN]["blemonitor"]
    bleupdater = BLEupdater(blemonitor, add_entities)
    hass.loop.create_task(bleupdater.async_run())
    _LOGGER.debug("Measuring sensor entry setup finished")
    # Return successful setup
    return True


# class BLEupdater(Thread):
class BLEupdater():
    """BLE monitor entities updater."""

    def __init__(self, blemonitor, add_entities):
        """Initiate BLE updater."""
        _LOGGER.debug("BLE sensors updater initialization")
        self.monitor = blemonitor
        self.dataqueue = blemonitor.dataqueue["measuring"].async_q
        self.config = blemonitor.config
        self.period = self.config[CONF_PERIOD]
        self.log_spikes = self.config[CONF_LOG_SPIKES]
        self.batt_entities = self.config[CONF_BATT_ENTITIES]
        self.add_entities = add_entities
        _LOGGER.debug("BLE sensors updater initialized")

    async def async_run(self):
        """Entities updater loop."""

        def temperature_limit(config, mac, temp):
            """Set limits for temperature measurement in °C or °F."""
            fmac = ':'.join(mac[i:i + 2] for i in range(0, len(mac), 2))

            if config[CONF_DEVICES]:
                for device in config[CONF_DEVICES]:
                    if fmac in device["mac"].upper():
                        if CONF_TEMPERATURE_UNIT in device:
                            if device[CONF_TEMPERATURE_UNIT] == TEMP_FAHRENHEIT:
                                temp_fahrenheit = temp * 9 / 5 + 32
                                return temp_fahrenheit
                        break
            return temp

        _LOGGER.debug("Entities updater loop started!")
        sensors_by_mac = {}
        sensors = []
        batt = {}  # batteries
        rssi = {}
        mibeacon_cnt = 0
        new_sensor_message = False
        ts_last = dt_util.now()
        ts_now = ts_last
        data = None
        await asyncio.sleep(0)
        while True:
            try:
                advevent = await asyncio.wait_for(self.dataqueue.get(), 1)
                if advevent is None:
                    _LOGGER.debug("Entities updater loop stopped")
                    return True
                data = advevent
                self.dataqueue.task_done()
            except asyncio.TimeoutError:
                pass
            if data:
                mibeacon_cnt += 1
                mac = data["mac"]
                # the RSSI value will be averaged for all valuable packets
                if mac not in rssi:
                    rssi[mac] = []
                rssi[mac].append(int(data["rssi"]))
                batt_attr = None
                sensortype = data["type"]
                t_i, h_i, m_i, c_i, i_i, f_i, cn_i, v_i, b_i = MMTS_DICT[sensortype][0]
                if mac not in sensors_by_mac:
                    sensors = []
                    if t_i != 9:
                        sensors.insert(t_i, TemperatureSensor(self.config, mac, sensortype))
                    if h_i != 9:
                        sensors.insert(h_i, HumiditySensor(self.config, mac, sensortype))
                    if m_i != 9:
                        sensors.insert(m_i, MoistureSensor(self.config, mac, sensortype))
                    if c_i != 9:
                        sensors.insert(c_i, ConductivitySensor(self.config, mac, sensortype))
                    if i_i != 9:
                        sensors.insert(i_i, IlluminanceSensor(self.config, mac, sensortype))
                    if f_i != 9:
                        sensors.insert(f_i, FormaldehydeSensor(self.config, mac, sensortype))
                    if cn_i != 9:
                        sensors.insert(cn_i, ConsumableSensor(self.config, mac, sensortype))
                    if (v_i != 9) and "voltage" in data:
                        # only add voltage sensor if available in data
                        try:
                            sensors.insert(v_i, VoltageSensor(self.config, mac, sensortype))
                        except IndexError:
                            pass
                    if self.batt_entities and (b_i != 9):
                        sensors.insert(b_i, BatterySensor(self.config, mac, sensortype))
                    if len(sensors) != 0:
                        sensors_by_mac[mac] = sensors
                        self.add_entities(sensors)
                else:
                    sensors = sensors_by_mac[mac]

                if data["data"] is False:
                    data = None
                    continue

                # store found readings per device
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
                # measuring sensors
                if "temperature" in data:
                    # dirty hack for kettle temperature data
                    if sensortype in KETTLES:
                        entity = sensors[t_i]
                        entity.collect(data, batt_attr)
                        if entity.ready_for_update is True:
                            entity.rssi_values = rssi[mac].copy()
                            entity.async_schedule_update_ha_state(True)
                            rssi[mac].clear()
                            entity.pending_update = False
                    else:
                        if (
                            temperature_limit(self.config, mac, CONF_TMAX)
                            >= data["temperature"]
                            >= temperature_limit(self.config, mac, CONF_TMIN)
                        ):
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
                            "Humidity spike: %s (%s)",
                            data["humidity"],
                            mac,
                        )
                if "conductivity" in data:
                    sensors[c_i].collect(data, batt_attr)
                if "moisture" in data:
                    sensors[m_i].collect(data, batt_attr)
                if "illuminance" in data:
                    try:
                        sensors[i_i].collect(data, batt_attr)
                    except IndexError:
                        # pass for dummy sensor of MJYD02YL
                        pass
                if "formaldehyde" in data:
                    sensors[f_i].collect(data, batt_attr)
                if "consumable" in data:
                    sensors[cn_i].collect(data, batt_attr)
                if "voltage" in data:
                    try:
                        sensors[v_i].collect(data, batt_attr)
                    except IndexError:
                        if new_sensor_message is False:
                            _LOGGER.warning(
                                "New voltage sensor found with MAC address %s. "
                                "Manually reload ble_monitor in the integration "
                                "menu to add voltage sensor and make sure you "
                                "use only one advertisement type (not all)", mac
                            )
                            new_sensor_message = True
                        pass
                data = None
            ts_now = dt_util.now()
            if ts_now - ts_last < timedelta(seconds=self.period):
                continue
            ts_last = ts_now
            # restarting scanner
            self.monitor.restart()
            # for every updated device
            for mac, elist in sensors_by_mac.items():
                for entity in elist:
                    if entity.pending_update is True:
                        if entity.ready_for_update is True:
                            entity.rssi_values = rssi[mac].copy()
                            entity.async_schedule_update_ha_state(True)
            for mac in rssi:
                rssi[mac].clear()

            _LOGGER.debug(
                "%i MiBeacon BLE ADV messages processed for %i measuring device(s).",
                mibeacon_cnt,
                len(sensors_by_mac),
            )
            mibeacon_cnt = 0


class MeasuringSensor(RestoreEntity):
    """Base class for measuring sensor entity."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        self.ready_for_update = False
        self._config = config
        self._mac = mac
        self._fmac = ":".join(self._mac[i:i + 2] for i in range(0, len(self._mac), 2))
        self._name = ""
        self._state = None
        self._unit_of_measurement = ""
        self._device_settings = self.get_device_settings()
        self._device_name = self._device_settings["name"]
        self._device_class = None
        self._device_type = devtype
        self._device_manufacturer = MANUFACTURER_DICT[devtype]
        self._device_state_attributes = {}
        self._device_state_attributes["sensor type"] = devtype
        self._device_state_attributes["mac address"] = self._fmac
        self._unique_id = ""
        self._measurement = "measurement"
        self._measurements = []
        self.rssi_values = []
        self.pending_update = False
        self._rdecimals = config[CONF_DECIMALS]
        self._jagged = False
        self._fmdh_dec = 0
        self._rounding = config[CONF_ROUNDING]
        self._use_median = config[CONF_USE_MEDIAN]
        self._restore_state = config[CONF_RESTORE_STATE]
        self._err = None

    async def async_added_to_hass(self):
        """Handle entity which will be added."""
        _LOGGER.debug("async_added_to_hass called for %s", self.name)
        await super().async_added_to_hass()

        # Restore the old state if available
        if self._restore_state is False:
            self.ready_for_update = True
            return
        old_state = await self.async_get_last_state()
        if not old_state:
            self.ready_for_update = True
            return
        try:
            self._unit_of_measurement = old_state.unit_of_measurement
        except AttributeError:
            pass
        self._state = old_state.state
        if "median" in old_state.attributes:
            self._device_state_attributes["median"] = old_state.attributes["median"]
        if "mean" in old_state.attributes:
            self._device_state_attributes["mean"] = old_state.attributes["mean"]
        if "last median of" in old_state.attributes:
            self._device_state_attributes["last median of"] = old_state.attributes["last median of"]
            self._state = old_state.attributes["median"]
        if "last mean of" in old_state.attributes:
            self._device_state_attributes["last mean of"] = old_state.attributes["last mean of"]
            self._state = old_state.attributes["mean"]
        if "rssi" in old_state.attributes:
            self._device_state_attributes["rssi"] = old_state.attributes["rssi"]
        if "last packet id" in old_state.attributes:
            self._device_state_attributes["last packet id"] = old_state.attributes["last packet id"]
        if ATTR_BATTERY_LEVEL in old_state.attributes:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = old_state.attributes[ATTR_BATTERY_LEVEL]
        self.ready_for_update = True

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
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {
                # Unique identifiers within a specific domain
                (DOMAIN, self._device_state_attributes["mac address"])
            },
            "name": self._device_name,
            "model": self._device_type,
            "manufacturer": self._device_manufacturer,
        }

    @property
    def force_update(self):
        """Force update."""
        return True

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        if self._jagged is True:
            self._measurements.append(int(data[self._measurement]))
        else:
            self._measurements.append(data[self._measurement])
        self._device_state_attributes["last packet id"] = data["packet"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    async def async_update(self):
        """Update sensor state and attributes."""
        textattr = ""
        rdecimals = self._rdecimals
        # formaldehyde decimals workaround
        if self._fmdh_dec > 0:
            rdecimals = self._fmdh_dec
        try:
            measurements = self._measurements
            if self._rounding:
                state_median = round(sts.median(measurements), rdecimals)
                state_mean = round(sts.mean(measurements), rdecimals)
            else:
                state_median = sts.median(measurements)
                state_mean = sts.mean(measurements)
            if self._use_median:
                textattr = "last median of"
                self._state = state_median
            else:
                textattr = "last mean of"
                self._state = state_mean
            self._device_state_attributes[textattr] = len(measurements)
            self._measurements.clear()
            self._device_state_attributes["median"] = state_median
            self._device_state_attributes["mean"] = state_mean
            self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
            self.rssi_values.clear()
        except (AttributeError, AssertionError):
            _LOGGER.debug("Sensor %s not yet ready for update", self._name)
        except ZeroDivisionError as err:
            self._err = err
        except IndexError as err:
            self._err = err
        except RuntimeError as err:
            self._err = err
        if self._err:
            _LOGGER.error("Sensor %s (%s) update error: %s", self._name, self._device_type, self._err)
        self.pending_update = False

    def get_device_settings(self):
        """Set device settings."""
        device_settings = {}

        # initial setup of device settings equal to integration settings
        dev_name = self._mac
        # in UI mode device name is equal to mac (but can be overwritten in UI)
        # in YAML mode device name is taken from config
        # when changing from YAML mode to UI mode, we keep using the unique_id as device name from YAML
        id_selector = CONF_UNIQUE_ID
        if "ids_from_name" in self._config:
            id_selector = CONF_NAME

        # overrule settings with device setting if available
        if self._config[CONF_DEVICES]:
            for device in self._config[CONF_DEVICES]:
                if self._fmac in device["mac"].upper():
                    if id_selector in device:
                        # get device name (from YAML config)
                        dev_name = device[id_selector]
        device_settings = {
            "name": dev_name,
        }
        _LOGGER.debug(
            "Sensor device with mac address %s has the following settings. "
            "Name: %s. ",
            self._fmac,
            device_settings["name"]
        )
        return device_settings


class TemperatureSensor(MeasuringSensor):
    """Representation of a sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "temperature"
        self._name = "ble temperature {}".format(self._device_name)
        self._unique_id = "t_" + self._device_name
        self._unit_of_measurement = self.get_temperature_unit()
        self._device_class = DEVICE_CLASS_TEMPERATURE

    def get_temperature_unit(self):
        """Set temperature unit to °C or °F."""
        fmac = ":".join(self._mac[i:i + 2] for i in range(0, len(self._mac), 2))

        if self._config[CONF_DEVICES]:
            for device in self._config[CONF_DEVICES]:
                if fmac in device["mac"].upper():
                    if CONF_TEMPERATURE_UNIT in device:
                        _LOGGER.debug(
                            "Temperature sensor with mac address %s is set to receive data in %s",
                            fmac,
                            device[CONF_TEMPERATURE_UNIT],
                        )
                        return device[CONF_TEMPERATURE_UNIT]
                    break
        _LOGGER.debug(
            "Temperature sensor with mac address %s is set to receive data in °C",
            fmac,
        )
        return TEMP_CELSIUS


class HumiditySensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "humidity"
        self._name = "ble humidity {}".format(self._device_name)
        self._unique_id = "h_" + self._device_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = DEVICE_CLASS_HUMIDITY
        # LYWSD03MMC / MHO-C401 "jagged" humidity workaround
        if devtype in ('LYWSD03MMC', 'MHO-C401'):
            self._jagged = True


class MoistureSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "moisture"
        self._name = "ble moisture {}".format(self._device_name)
        self._unique_id = "m_" + self._device_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = DEVICE_CLASS_HUMIDITY


class ConductivitySensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "conductivity"
        self._name = "ble conductivity {}".format(self._device_name)
        self._unique_id = "c_" + self._device_name
        self._unit_of_measurement = CONDUCTIVITY
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:flash-circle"


class IlluminanceSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "illuminance"
        self._name = "ble illuminance {}".format(self._device_name)
        self._unique_id = "l_" + self._device_name
        self._unit_of_measurement = "lx"
        self._device_class = DEVICE_CLASS_ILLUMINANCE


class FormaldehydeSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "formaldehyde"
        self._name = "ble formaldehyde {}".format(self._device_name)
        self._unique_id = "f_" + self._device_name
        self._unit_of_measurement = "mg/m³"
        self._device_class = None
        self._fmdh_dec = 3

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:chemical-weapon"


class VoltageSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "voltage"
        self._name = "ble voltage {}".format(self._device_name)
        self._unique_id = "v_" + self._device_name
        self._unit_of_measurement = VOLT
        self._device_class = DEVICE_CLASS_VOLTAGE


class BatterySensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "battery"
        self._name = "ble battery {}".format(self._device_name)
        self._unique_id = "batt_" + self._device_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = DEVICE_CLASS_BATTERY

    def collect(self, data, batt_attr=None):
        """Battery measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        self.pending_update = True

    async def async_update(self):
        """Update sensor state and attributes."""
        self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False


class ConsumableSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "consumable"
        self._name = "ble consumable {}".format(self._device_name)
        self._unique_id = "cn_" + self._device_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:mdi-recycle-variant"

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    async def async_update(self):
        """Update."""
        self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False
