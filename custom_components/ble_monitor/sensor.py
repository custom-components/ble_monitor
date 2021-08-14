"""Passive BLE monitor sensor platform."""
from datetime import timedelta
import asyncio
import logging
import statistics as sts

from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    CONDUCTIVITY,
    CONF_DEVICES,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    CONF_UNIQUE_ID,
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_VOLTAGE,
    ELECTRIC_POTENTIAL_VOLT,
    ENERGY_KILO_WATT_HOUR,
    PERCENTAGE,
    POWER_KILO_WATT,
    PRESSURE_HPA,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT
)

from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.components.sensor import SensorEntity, STATE_CLASS_MEASUREMENT
import homeassistant.util.dt as dt_util

from .const import (
    CONF_DECIMALS,
    CONF_PERIOD,
    CONF_LOG_SPIKES,
    CONF_USE_MEDIAN,
    CONF_RESTORE_STATE,
    CONF_DEVICE_DECIMALS,
    CONF_DEVICE_USE_MEDIAN,
    CONF_DEVICE_RESTORE_STATE,
    CONF_DEVICE_RESET_TIMER,
    CONF_TMIN,
    CONF_TMAX,
    CONF_TMIN_KETTLES,
    CONF_TMAX_KETTLES,
    CONF_HMIN,
    CONF_HMAX,
    DEFAULT_DEVICE_RESET_TIMER,
    KETTLES,
    MANUFACTURER_DICT,
    MEASUREMENT_DICT,
    SENSOR_DICT,
    RENAMED_MODEL_DICT,
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
    hass.loop.create_task(bleupdater.async_run(hass))
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
        self.add_entities = add_entities
        _LOGGER.debug("BLE sensors updater initialized")

    async def async_run(self, hass):
        """Entities updater loop."""

        async def async_add_sensor(mac, sensortype, firmware):
            averaging_sensors = MEASUREMENT_DICT[sensortype][0]
            instant_sensors = MEASUREMENT_DICT[sensortype][1]
            device_sensors = averaging_sensors + instant_sensors
            if mac not in sensors_by_mac:
                sensors = []
                for sensor in device_sensors:
                    sensors.insert(
                        device_sensors.index(sensor),
                        globals()[SENSOR_DICT[sensor]](self.config, mac, sensortype, firmware),
                    )
                if len(sensors) != 0:
                    sensors_by_mac[mac] = sensors
                    self.add_entities(sensors)
            else:
                sensors = sensors_by_mac[mac]
            return sensors

        _LOGGER.debug("Entities updater loop started!")
        sensors_by_mac = {}
        sensors = []
        batt = {}  # batteries
        rssi = {}
        ble_adv_cnt = 0
        ts_last = dt_util.now()
        ts_now = ts_last
        ts_start = ts_last
        data = None
        await asyncio.sleep(0)

        # Set up sensors of configured devices on startup when sensortype is available in device registry
        if self.config[CONF_DEVICES]:
            dev_registry = await hass.helpers.device_registry.async_get_registry()
            for device in self.config[CONF_DEVICES]:
                mac = device["mac"]

                # get sensortype and firmware from device registry to setup sensor
                dev = dev_registry.async_get_device({(DOMAIN, mac)}, set())
                if dev:
                    mac = mac.replace(":", "")
                    sensortype = dev.model
                    # migrate to new model name if changed
                    if dev.model in RENAMED_MODEL_DICT.keys():
                        sensortype = RENAMED_MODEL_DICT[dev.model]
                    firmware = dev.sw_version
                    if sensortype and firmware:
                        sensors = await async_add_sensor(mac, sensortype, firmware)
                    else:
                        continue
                else:
                    pass
        else:
            sensors = []

        # Set up new sensors when first BLE advertisement is received
        sensors = []
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
                _LOGGER.debug("Data measuring sensor received: %s", data)
                ble_adv_cnt += 1
                mac = data["mac"]
                # the RSSI value will be averaged for all valuable packets
                if mac not in rssi:
                    rssi[mac] = []
                rssi[mac].append(int(data["rssi"]))
                batt_attr = None
                sensortype = data["type"]
                # migrate to new model name if changed
                if data["type"] in RENAMED_MODEL_DICT.keys():
                    sensortype = RENAMED_MODEL_DICT[data["type"]]
                firmware = data["firmware"]
                averaging_sensors = MEASUREMENT_DICT[sensortype][0]
                instant_sensors = MEASUREMENT_DICT[sensortype][1]
                device_sensors = averaging_sensors + instant_sensors
                sensors = await async_add_sensor(mac, sensortype, firmware)
                if data["data"] is False:
                    data = None
                    continue

                # battery attribute
                if "battery" in device_sensors:
                    if "battery" in data:
                        batt[mac] = int(data["battery"])
                        batt_attr = batt[mac]
                    else:
                        try:
                            batt_attr = batt[mac]
                        except KeyError:
                            batt_attr = None

                # store found readings per device
                for measurement in device_sensors:
                    if measurement in data:
                        entity = sensors[device_sensors.index(measurement)]
                        entity.collect(data, batt_attr)
                        if measurement in instant_sensors or ts_now - ts_start < timedelta(seconds=self.period):
                            # instant measurements are updated instantly
                            if entity.pending_update is True:
                                if entity.ready_for_update is True:
                                    entity.rssi_values = rssi[mac].copy()
                                    entity.async_schedule_update_ha_state(True)
                                    entity.pending_update = False
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
                "%i BLE ADV messages processed for %i measuring device(s).",
                ble_adv_cnt,
                len(sensors_by_mac),
            )
            ble_adv_cnt = 0


class BaseSensor(RestoreEntity, SensorEntity):
    """Base class for all sensor entities."""

    # BaseSensor
    # |--MeasuringSensor
    # |  |--TemperatureSensor
    # |  |--TemperatureOutdoorSensor
    # |  |--HumiditySensor
    # |  |--HumidityOutdoorSensor
    # |  |--MoistureSensor
    # |  |--PressureSensor
    # |  |--ConductivitySensor
    # |  |--IlluminanceSensor
    # |  |--FormaldehydeSensor
    # |  |--VoltageSensor
    # |  |--BatterySensor
    # |--InstantUpdateSensor
    # |  |--ConsumableSensor
    # |  |--AccelerationSensor
    # |  |--ToothbrushModeSensor
    # |  |--WeightSensor
    # |  |--NonStabilizedWeightSensor
    # |  |--ImpedanceSensor
    # |  |--EnergySensor
    # |  |--PowerSensor
    # |  |--SwitchSensor
    # |  |  |--SingleSwitchSensor
    # |  |  |--DoubleSwitchLeftSensor
    # |  |  |--DoubleSwitchRightSensor
    # |  |  |--TripleSwitchLeftSensor
    # |  |  |--TripleSwitchMiddleSensor
    # |  |  |--TripleSwitchRightSensor
    # |  |  |--ButtonSensor
    # |  |  |--DimmerSensor
    # |  |--BaseRemoteSensor
    # |  |  |--RemoteSensor
    # |  |  |--FanRemoteSensor
    # |  |  |--VentilatorFanRemoteSensor
    # |  |  |--BathroomHeaterRemoteSensor
    # |  |--VolumeDispensedSensor
    # |  |  |--VolumeDispensedPort1Sensor
    # |  |  |--VolumeDispensedPort2Sensor

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        self.ready_for_update = False
        self._config = config
        self._mac = mac
        self._fmac = ":".join(self._mac[i:i + 2] for i in range(0, len(self._mac), 2))
        self._name = ""
        self._state = None
        self._state_class = None
        self._unit_of_measurement = ""
        self._device_settings = self.get_device_settings()
        self._device_name = self._device_settings["name"]
        self._device_class = None
        self._device_type = devtype
        self._device_firmware = firmware
        self._device_manufacturer = MANUFACTURER_DICT[devtype]
        self._device_state_attributes = {}
        self._device_state_attributes["sensor type"] = devtype
        self._device_state_attributes["mac address"] = self._fmac
        self._unique_id = ""
        self._measurement = "measurement"
        self._measurements = []
        self.rssi_values = []
        self.pending_update = False
        self._restore_state = self._device_settings["restore state"]
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
        if "firmware" in old_state.attributes:
            self._device_state_attributes["firmware"] = old_state.attributes["firmware"]
        if "last packet id" in old_state.attributes:
            self._device_state_attributes["last packet id"] = old_state.attributes["last packet id"]
        if "last button press" in old_state.attributes:
            self._device_state_attributes["last button press"] = old_state.attributes["last button press"]
        if "last remote button pressed" in old_state.attributes:
            self._device_state_attributes["last remote button pressed"] = old_state.attributes["last remote button pressed"]
        if "last type of press" in old_state.attributes:
            self._device_state_attributes["last type of press"] = old_state.attributes["last type of press"]
        if "dimmer value" in old_state.attributes:
            self._device_state_attributes["dimmer value"] = old_state.attributes["dimmer value"]
        if "constant" in old_state.attributes:
            self._device_state_attributes["constant"] = old_state.attributes["constant"]
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
    def state_class(self):
        """Return type of state."""
        return self._state_class

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
            "sw_version": self._device_firmware,
            "manufacturer": self._device_manufacturer,
        }

    @property
    def force_update(self):
        """Force update."""
        return True

    def get_device_settings(self):
        """Set device settings."""
        device_settings = {}

        # initial setup of device settings equal to integration settings
        dev_name = self._mac
        dev_temperature_unit = TEMP_CELSIUS
        dev_decimals = self._config[CONF_DECIMALS]
        dev_use_median = self._config[CONF_USE_MEDIAN]
        dev_restore_state = self._config[CONF_RESTORE_STATE]
        dev_reset_timer = DEFAULT_DEVICE_RESET_TIMER

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
                    if CONF_TEMPERATURE_UNIT in device:
                        dev_temperature_unit = device[CONF_TEMPERATURE_UNIT]
                    if CONF_DEVICE_DECIMALS in device:
                        if isinstance(device[CONF_DEVICE_DECIMALS], int):
                            dev_decimals = device[CONF_DEVICE_DECIMALS]
                        else:
                            dev_decimals = self._config[CONF_DECIMALS]
                    if CONF_DEVICE_USE_MEDIAN in device:
                        if isinstance(device[CONF_DEVICE_USE_MEDIAN], bool):
                            dev_use_median = device[CONF_DEVICE_USE_MEDIAN]
                        else:
                            dev_use_median = self._config[CONF_USE_MEDIAN]
                    if CONF_DEVICE_RESTORE_STATE in device:
                        if isinstance(device[CONF_DEVICE_RESTORE_STATE], bool):
                            dev_restore_state = device[CONF_DEVICE_RESTORE_STATE]
                        else:
                            dev_restore_state = self._config[CONF_RESTORE_STATE]
                    if CONF_DEVICE_RESET_TIMER in device:
                        dev_reset_timer = device[CONF_DEVICE_RESET_TIMER]
        device_settings = {
            "name": dev_name,
            "temperature unit": dev_temperature_unit,
            "decimals": dev_decimals,
            "use median": dev_use_median,
            "restore state": dev_restore_state,
            "reset timer": dev_reset_timer
        }
        _LOGGER.debug(
            "Sensor device with mac address %s has the following settings. "
            "Name: %s. "
            "Temperature unit: %s. "
            "Decimals: %s. "
            "Use Median: %s. "
            "Restore state: %s. "
            "Reset Timer: %s.",
            self._fmac,
            device_settings["name"],
            device_settings["temperature unit"],
            device_settings["decimals"],
            device_settings["use median"],
            device_settings["restore state"],
            device_settings["reset timer"],
        )
        return device_settings


class MeasuringSensor(BaseSensor):
    """Base class for measuring sensor entities."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._rdecimals = self._device_settings["decimals"]
        self._jagged = False
        self._fmdh_dec = 0
        self._use_median = self._device_settings["use median"]
        self._state_class = STATE_CLASS_MEASUREMENT

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._measurements.append(data[self._measurement])
        self._device_state_attributes["sensor type"] = data["type"]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
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
            state_median = round(sts.median(measurements), rdecimals)
            state_mean = round(sts.mean(measurements), rdecimals)
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


class TemperatureSensor(MeasuringSensor):
    """Representation of a Temperature sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "temperature"
        self._name = "ble temperature {}".format(self._device_name)
        self._unique_id = "t_" + self._device_name
        self._unit_of_measurement = self._device_settings["temperature unit"]
        self._device_class = DEVICE_CLASS_TEMPERATURE

        self._temp_min = CONF_TMIN_KETTLES if devtype in KETTLES else CONF_TMIN
        self._temp_max = CONF_TMAX_KETTLES if devtype in KETTLES else CONF_TMAX
        self._lower_temp_limit = self.temperature_limit(config, mac, self._temp_min)
        self._upper_temp_limit = self.temperature_limit(config, mac, self._temp_max)
        self._log_spikes = config[CONF_LOG_SPIKES]

    def temperature_limit(self, config, mac, temp):
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

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        if not self._lower_temp_limit <= data[self._measurement] <= self._upper_temp_limit:
            if self._log_spikes:
                _LOGGER.error("Temperature spike: %s (%s)", data[self._measurement], self._mac)
            self.pending_update = False
            return
        self._measurements.append(data[self._measurement])
        self._device_state_attributes["sensor type"] = data["type"]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class TemperatureOutdoorSensor(TemperatureSensor):
    """Representation of an outdoor temperature sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "temperature outdoor"
        self._name = "ble temperature outdoor {}".format(self._device_name)
        self._unique_id = "t_outdoor_" + self._device_name
        self._unit_of_measurement = self._device_settings["temperature unit"]
        self._device_class = DEVICE_CLASS_TEMPERATURE

        self._lower_temp_limit = self.temperature_limit(config, mac, self._temp_min)
        self._upper_temp_limit = self.temperature_limit(config, mac, self._temp_max)
        self._log_spikes = config[CONF_LOG_SPIKES]


class HumiditySensor(MeasuringSensor):
    """Representation of a Humidity sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "humidity"
        self._name = "ble humidity {}".format(self._device_name)
        self._unique_id = "h_" + self._device_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = DEVICE_CLASS_HUMIDITY
        self._log_spikes = config[CONF_LOG_SPIKES]
        # LYWSD03MMC / MHO-C401 "jagged" humidity workaround
        if devtype in ('LYWSD03MMC', 'MHO-C401'):
            if self._device_firmware is not None:
                if self._device_firmware[0:6] == "Xiaomi":
                    self._jagged = True

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        if not CONF_HMIN <= data[self._measurement] <= CONF_HMAX:
            if self._log_spikes:
                _LOGGER.error("Humidity spike: %s (%s)", data[self._measurement], self._mac)
            self.pending_update = False
            return
        if self._jagged is True:
            self._measurements.append(int(data[self._measurement]))
        else:
            self._measurements.append(data[self._measurement])
        self._device_state_attributes["sensor type"] = data["type"]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class HumidityOutdoorSensor(HumiditySensor):
    """Representation of an Outdoor Humidity sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "humidity outdoor"
        self._name = "ble humidity outdoor {}".format(self._device_name)
        self._unique_id = "h_outdoor_" + self._device_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = DEVICE_CLASS_HUMIDITY
        self._log_spikes = config[CONF_LOG_SPIKES]


class MoistureSensor(MeasuringSensor):
    """Representation of a Moisture sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "moisture"
        self._name = "ble moisture {}".format(self._device_name)
        self._unique_id = "m_" + self._device_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = DEVICE_CLASS_HUMIDITY


class PressureSensor(MeasuringSensor):
    """Representation of a Pressure sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "pressure"
        self._name = "ble pressure {}".format(self._device_name)
        self._unique_id = "p_" + self._device_name
        self._unit_of_measurement = PRESSURE_HPA
        self._device_class = DEVICE_CLASS_PRESSURE


class ConductivitySensor(MeasuringSensor):
    """Representation of a Conductivity sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
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
    """Representation of a Illuminance sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "illuminance"
        self._name = "ble illuminance {}".format(self._device_name)
        self._unique_id = "l_" + self._device_name
        self._unit_of_measurement = "lx"
        self._device_class = DEVICE_CLASS_ILLUMINANCE


class FormaldehydeSensor(MeasuringSensor):
    """Representation of a Formaldehyde sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
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
    """Representation of a Voltage sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "voltage"
        self._name = "ble voltage {}".format(self._device_name)
        self._unique_id = "v_" + self._device_name
        self._unit_of_measurement = ELECTRIC_POTENTIAL_VOLT
        self._device_class = DEVICE_CLASS_VOLTAGE


class BatterySensor(MeasuringSensor):
    """Representation of a Battery sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
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
        self._device_state_attributes["sensor type"] = data["type"]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        self.pending_update = True

    async def async_update(self):
        """Update sensor state and attributes."""
        self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False


class InstantUpdateSensor(BaseSensor):
    """Base class for instant updating sensor entity"""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._reset_timer = self._device_settings["reset timer"]
        self._state_class = STATE_CLASS_MEASUREMENT

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._measurement]
        self._device_state_attributes["sensor type"] = data["type"]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    async def async_update(self):
        """Update sensor state and attributes."""
        self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False


class AccelerationSensor(InstantUpdateSensor):
    """Representation of a Acceleration sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "acceleration"
        self._name = "ble acceleration {}".format(self._device_name)
        self._unique_id = "ac_" + self._device_name
        self._unit_of_measurement = "mG"
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:axis-arrow"

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._measurement]
        self._device_state_attributes["sensor type"] = data["type"]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        self._device_state_attributes["acceleration x"] = data["acceleration x"]
        self._device_state_attributes["acceleration y"] = data["acceleration y"]
        self._device_state_attributes["acceleration z"] = data["acceleration z"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class ConsumableSensor(InstantUpdateSensor):
    """Representation of a Consumable sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "consumable"
        self._name = "ble consumable {}".format(self._device_name)
        self._unique_id = "cn_" + self._device_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:recycle-variant"


class ToothbrushModeSensor(InstantUpdateSensor):
    """Representation of a Toothbrush mode sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "toothbrush mode"
        self._name = "ble toothbrush mode {}".format(self._device_name)
        self._unique_id = "to_" + self._device_name
        self._unit_of_measurement = None
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:toothbrush-electric"


class WeightSensor(InstantUpdateSensor):
    """Representation of a Weight sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "weight"
        self._name = "ble weight {}".format(self._device_name)
        self._unique_id = "w_" + self._device_name
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:scale-bathroom"

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        if "weight unit" in data:
            self._unit_of_measurement = data["weight unit"]
        else:
            self._unit_of_measurement = None
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class NonStabilizedWeightSensor(InstantUpdateSensor):
    """Representation of a non-stabilized Weight sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "non-stabilized weight"
        self._name = "ble non-stabilized weight {}".format(self._device_name)
        self._unique_id = "nw_" + self._device_name
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:scale-bathroom"

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        self._device_state_attributes["stabilized"] = True if data["stabilized"] else False
        self._device_state_attributes["weight removed"] = True if data["weight removed"] else False
        if "weight unit" in data:
            self._unit_of_measurement = data["weight unit"]
        else:
            self._unit_of_measurement = None
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class ImpedanceSensor(InstantUpdateSensor):
    """Representation of a Impedance sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "impedance"
        self._name = "ble impedance {}".format(self._device_name)
        self._unique_id = "im_" + self._device_name
        self._unit_of_measurement = "Ohm"
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:omega"


class EnergySensor(InstantUpdateSensor):
    """Representation of an Energy sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "energy"
        self._name = "ble energy {}".format(self._device_name)
        self._unique_id = "e_" + self._device_name
        self._device_class = DEVICE_CLASS_ENERGY
        self._rdecimals = self._device_settings["decimals"]

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = round(data[self._measurement], self._rdecimals)
        self._device_state_attributes["sensor type"] = data["type"]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        if "energy unit" in data:
            self._unit_of_measurement = data["energy unit"]
        else:
            self._unit_of_measurement = ENERGY_KILO_WATT_HOUR
        if "constant" in data:
            self._device_state_attributes["constant"] = data["constant"]
        if "light level" in data:
            self._device_state_attributes["light level"] = data["light level"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class PowerSensor(InstantUpdateSensor):
    """Representation of a Power sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "power"
        self._name = "ble power {}".format(self._device_name)
        self._unique_id = "pow_" + self._device_name
        self._device_class = DEVICE_CLASS_POWER
        self._rdecimals = self._device_settings["decimals"]

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = round(data[self._measurement], self._rdecimals)
        self._device_state_attributes["sensor type"] = data["type"]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        if "power unit" in data:
            self._unit_of_measurement = data["power unit"]
        else:
            self._unit_of_measurement = POWER_KILO_WATT
        if "constant" in data:
            self._device_state_attributes["constant"] = data["constant"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class SwitchSensor(InstantUpdateSensor):
    """Representation of a Switch sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = ""
        self._button = ""
        self._state_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:gesture-tap-button"

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        if data[self._button] == "toggle":
            self._state = data[self._measurement]
        else:
            self.pending_update = False
            return
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        self._device_state_attributes["last press"] = self._state
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    def reset_state(self, event=None):
        """Reset state of the sensor."""
        self._state = "no press"
        self.schedule_update_ha_state(False)

    async def async_update(self):
        """Update."""
        self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        if self._reset_timer > 0:
            _LOGGER.debug("Reset timer is set to: %i seconds", self._reset_timer)
            async_call_later(self.hass, self._reset_timer, self.reset_state)
        self.rssi_values.clear()
        self.pending_update = False


class SingleSwitchSensor(SwitchSensor):
    """Representation of a Switch sensor (single button)."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "button switch"
        self._button = "one btn switch"
        self._name = "ble switch {}".format(self._device_name)
        self._unique_id = "switch_" + self._device_name


class DoubleSwitchLeftSensor(SwitchSensor):
    """Representation of a 2 button Switch sensor (left button)."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "button switch"
        self._button = "two btn switch left"
        self._name = "ble left switch {}".format(self._device_name)
        self._unique_id = "left_switch_" + self._device_name


class DoubleSwitchRightSensor(SwitchSensor):
    """Representation of a 2 button Switch sensor (right button)."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "button switch"
        self._button = "two btn switch right"
        self._name = "ble right switch {}".format(self._device_name)
        self._unique_id = "right_switch_" + self._device_name


class TripleSwitchLeftSensor(SwitchSensor):
    """Representation of a 3 button Switch sensor (left button)."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "button switch"
        self._button = "three btn switch left"
        self._name = "ble left switch {}".format(self._device_name)
        self._unique_id = "left_switch_" + self._device_name


class TripleSwitchMiddleSensor(SwitchSensor):
    """Representation of a 3 button Switch sensor (middle button)."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "button switch"
        self._button = "three btn switch middle"
        self._name = "ble middle switch {}".format(self._device_name)
        self._unique_id = "middle_switch_" + self._device_name


class TripleSwitchRightSensor(SwitchSensor):
    """Representation of a 3 button Switch sensor (right button)."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "button switch"
        self._button = "three btn switch right"
        self._name = "ble right switch {}".format(self._device_name)
        self._unique_id = "right_switch_" + self._device_name


class ButtonSensor(SwitchSensor):
    """Representation of a Button sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "button"
        self._name = "ble button {}".format(self._device_name)
        self._unique_id = "bu_" + self._device_name

    def collect(self, data, batt_attr=None):
        """Measurement collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class DimmerSensor(SwitchSensor):
    """Representation of a Dimmer sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._button = "button"
        self._dimmer = "dimmer"
        self._name = "ble dimmer {}".format(self._device_name)
        self._unique_id = "di_" + self._device_name

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:rotate-right"

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._button] + " " + str(data[self._dimmer]) + " steps"
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        self._device_state_attributes["dimmer value"] = data[self._dimmer]
        self._device_state_attributes["last type of press"] = data[self._button]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class BaseRemoteSensor(InstantUpdateSensor):
    """Representation of a Remote sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._button = ""
        self._remote = ""
        self._name = ""
        self._unique_id = ""

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:remote"

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._button] + " " + data[self._remote]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        self._device_state_attributes["last remote button pressed"] = data[self._remote]
        self._device_state_attributes["last type of press"] = data["button"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    def reset_state(self, event=None):
        """Reset state of the sensor."""
        self._state = "no press"
        self.schedule_update_ha_state(False)

    async def async_update(self):
        """Update."""
        self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        if self._reset_timer > 0:
            _LOGGER.debug("Reset timer is set to: %i seconds", self._reset_timer)
            async_call_later(self.hass, self._reset_timer, self.reset_state)
        self.rssi_values.clear()
        self.pending_update = False


class RemoteSensor(BaseRemoteSensor):
    """Representation of a Remote sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._button = "button"
        self._remote = "remote"
        self._name = "ble remote {}".format(self._device_name)
        self._unique_id = "re_" + self._device_name


class FanRemoteSensor(BaseRemoteSensor):
    """Representation of a Fan Remote sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._button = "button"
        self._remote = "fan remote"
        self._name = "ble fan remote {}".format(self._device_name)
        self._unique_id = "fr_" + self._device_name


class VentilatorFanRemoteSensor(BaseRemoteSensor):
    """Representation of a Ventilator Fan Remote sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._button = "button"
        self._remote = "ventilator fan remote"
        self._name = "ble ventilator fan remote {}".format(self._device_name)
        self._unique_id = "vr_" + self._device_name


class BathroomHeaterRemoteSensor(BaseRemoteSensor):
    """Representation of a Bathroom Heater Remote sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._button = "button"
        self._bathroom_heater_remote = "bathroom heater remote"
        self._name = "ble bathroom heater remote {}".format(self._device_name)
        self._unique_id = "br_" + self._device_name


class VolumeDispensedSensor(InstantUpdateSensor):
    """Representation of a Kegtron Volume dispensed sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._unit_of_measurement = "L"
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:keg"

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        self._device_state_attributes["volume start"] = data["volume start"]
        self._device_state_attributes["keg size"] = data["keg size"]
        self._device_state_attributes["port name"] = data["port name"]
        self._device_state_attributes["port state"] = data["port state"]
        self._device_state_attributes["port index"] = data["port index"]
        self.pending_update = True


class VolumeDispensedPort1Sensor(VolumeDispensedSensor):
    """Representation of a Kegtron Volume dispensed port 1 sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "volume dispensed port 1"
        self._name = "ble volume dispensed port 1 {}".format(self._device_name)
        self._unique_id = "vd_1_" + self._device_name


class VolumeDispensedPort2Sensor(VolumeDispensedSensor):
    """Representation of a Kegtron Volume dispensed port 2 sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "volume dispensed port 2"
        self._name = "ble volume dispensed port 2 {}".format(self._device_name)
        self._unique_id = "vd_2_" + self._device_name
