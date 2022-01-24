"""Passive BLE monitor sensor platform."""
from datetime import timedelta
import asyncio
import logging
import statistics as sts

from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    CONF_DEVICES,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    CONF_UNIQUE_ID,
    CONF_MAC,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)

from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.components.sensor import SensorEntity
import homeassistant.util.dt as dt_util

from .helper import (
    identifier_normalize,
    identifier_clean,
    detect_conf_type,
    dict_get_or,
    dict_get_or_normalize,
)

from .const import (
    CONF_DECIMALS,
    CONF_PERIOD,
    CONF_UUID,
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
    CONF_TMIN_PROBES,
    CONF_TMAX_PROBES,
    CONF_HMIN,
    CONF_HMAX,
    DEFAULT_DEVICE_RESET_TIMER,
    KETTLES,
    MANUFACTURER_DICT,
    MEASUREMENT_DICT,
    PROBES,
    RENAMED_MODEL_DICT,
    DOMAIN,
    SENSOR_TYPES,
    BLEMonitorSensorEntityDescription,
)

_LOGGER = logging.getLogger(__name__)

RESTORE_ATTRIBUTES = [
    "median",
    "mean",
    "last median of",
    "last mean of",
    "rssi",
    "firmware",
    "last packet id",
    "last button press",
    "last remote button pressed",
    "last type of press",
    "dimmer value",
    "constant",
    "volume start",
    "keg size",
    "port name",
    "port state",
    "port index",
    "impedance",
    "acceleration x",
    "acceleration y",
    "acceleration z",
    "light level",
    ATTR_BATTERY_LEVEL,
]


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
class BLEupdater:
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

        async def async_add_sensor(key, sensortype, firmware, manufacturer = None):
            averaging_sensors = MEASUREMENT_DICT[sensortype][0]
            instant_sensors = MEASUREMENT_DICT[sensortype][1]
            device_sensors = averaging_sensors + instant_sensors
            if key not in sensors_by_key:
                sensors = []
                for sensor in device_sensors:
                    description = [item for item in SENSOR_TYPES if item.key is sensor][
                        0
                    ]
                    sensors.insert(
                        device_sensors.index(sensor),
                        globals()[description.sensor_class](
                            self.config, key, sensortype, firmware, description, manufacturer
                        ),
                    )
                if len(sensors) != 0:
                    sensors_by_key[key] = sensors
                    self.add_entities(sensors)
            else:
                sensors = sensors_by_key[key]
            return sensors

        _LOGGER.debug("Entities updater loop started!")
        sensors_by_key = {}
        sensors = []
        batt = {}  # batteries
        rssi = {}  # rssi
        ble_adv_cnt = 0

        ts_now = dt_util.now()
        ts_restart = ts_now
        ts_last_update = ts_now
        period_cnt = 0

        data = None
        await asyncio.sleep(0)

        # Set up sensors of configured devices on startup when sensortype is available in device registry
        if self.config[CONF_DEVICES]:
            dev_registry = await hass.helpers.device_registry.async_get_registry()
            for device in self.config[CONF_DEVICES]:
                key = dict_get_or(device)

                # get sensortype and firmware from device registry to setup sensor
                dev = dev_registry.async_get_device({(DOMAIN, key.upper())}, set())
                if dev:
                    key = identifier_clean(key)
                    sensortype = dev.model
                    # migrate to new model name if changed
                    if dev.model in RENAMED_MODEL_DICT.keys():
                        sensortype = RENAMED_MODEL_DICT[dev.model]
                    firmware = dev.sw_version
                    if sensortype and firmware:
                        sensors = await async_add_sensor(key, sensortype, firmware, dev.manufacturer)
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
                key = dict_get_or(data)
                # the RSSI value will be averaged for all valuable packets
                if key not in rssi:
                    rssi[key] = []
                rssi[key].append(int(data["rssi"]))
                batt_attr = None
                sensortype = data["type"]
                # migrate to new model name if changed
                if data["type"] in RENAMED_MODEL_DICT.keys():
                    sensortype = RENAMED_MODEL_DICT[data["type"]]
                firmware = data["firmware"]
                manufacturer = data["manufacturer"] if "manufacturer" in data else None
                averaging_sensors = MEASUREMENT_DICT[sensortype][0]
                instant_sensors = MEASUREMENT_DICT[sensortype][1]
                device_sensors = averaging_sensors + instant_sensors
                sensors = await async_add_sensor(key, sensortype, firmware, manufacturer)
                if data["data"] is False:
                    data = None
                    continue

                # battery attribute
                if "battery" in device_sensors:
                    if "battery" in data:
                        batt[key] = int(data["battery"])
                        batt_attr = batt[key]
                    else:
                        try:
                            batt_attr = batt[key]
                        except KeyError:
                            batt_attr = None

                # store found readings per device
                for measurement in device_sensors:
                    if measurement in data:
                        entity = sensors[device_sensors.index(measurement)]
                        entity.collect(data, period_cnt, batt_attr)
                        if (
                            measurement in instant_sensors
                            or ts_now - ts_restart < timedelta(seconds=self.period)
                        ):
                            # instant measurements and measurements in the first period are updated instantly
                            if entity.pending_update is True:
                                if entity.ready_for_update is True:
                                    entity.rssi_values = rssi[key].copy()
                                    entity.async_schedule_update_ha_state(True)
                                    entity.pending_update = False
                data = None
            ts_now = dt_util.now()
            if ts_now - ts_last_update < timedelta(seconds=self.period):
                continue
            ts_last_update = ts_now
            period_cnt += 1
            # restarting scanner
            self.monitor.restart()
            # updating the state for every updated measureing device
            for key, elist in sensors_by_key.items():
                for entity in elist:
                    if entity.pending_update is True:
                        if entity.ready_for_update is True:
                            entity.rssi_values = rssi[key].copy()
                            entity.async_schedule_update_ha_state(True)
            for key in rssi:
                rssi[key].clear()

            _LOGGER.debug(
                "%i BLE ADV messages processed for %i measuring device(s)",
                ble_adv_cnt,
                len(sensors_by_key),
            )
            ble_adv_cnt = 0


class BaseSensor(RestoreEntity, SensorEntity):
    """Base class for all sensor entities."""

    # BaseSensor (Class)
    # |--MeasuringSensor (Class)
    # |  |--TemperatureSensor (Class)
    # |  |  |**temperature
    # |  |  |**temperature probe 1 till 6
    # |  |  |**temperature outdoor
    # |  |  |**temperature alarm
    # |  |--HumiditySensor (Class)
    # |  |  |**humidity
    # |  |  |**humidity outdoor
    # |  |**moisture
    # |  |**pressure
    # |  |**conductivity
    # |  |**illuminance
    # |  |**formaldehyde
    # |  |**dewpoint
    # |  |**rssi
    # |  |--BatterySensor (Class)
    # |  |  |**battery
    # |  |**voltage
    # |--InstantUpdateSensor (Class)
    # |  |**consumable
    # |  |--AccelerationSensor (Class)
    # |  |  |**acceleration
    # |  |--WeightSensor (Class)
    # |  |  |**weight
    # |  |  |**non-stabilized weight
    # |  |**MagneticFieldSensor
    # |  |**MagneticFieldDirectionSensor
    # |  |**ImpedanceSensor
    # |  |--EnergySensor (Class)
    # |  |  |**energy
    # |  |--PowerSensor (Class)
    # |  |  |**power
    # |  |--ButtonSensor (Class)
    # |  |  |**button
    # |  |--DimmerSensor (Class)
    # |  |  |**dimmer
    # |  |--SwitchSensor (Class)
    # |  |  |**one btn switch
    # |  |  |**two btn switch left
    # |  |  |**two btn switch right
    # |  |  |**three btn switch left
    # |  |  |**three btn switch middle
    # |  |  |**three btn switch right
    # |  |--BaseRemoteSensor (Class)
    # |  |  |**remote
    # |  |  |**fan remote
    # |  |  |**ventilator fan remote
    # |  |  |**bathroom heater remote
    # |  |--VolumeDispensedSensor (Class)
    # |  |  |**volume dispensed port 1
    # |  |  |**volume dispensed port 2

    # ** is a entity_descripiton key
    # -- is a Class

    def __init__(
        self,
        config,
        key: str,
        devtype: str,
        firmware: str,
        description: BLEMonitorSensorEntityDescription,
        manufacturer = None,
    ) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        self._config = config
        self._type = detect_conf_type(key)
        self._key = key
        self._fkey = identifier_normalize(key)
        self._state = None

        self._device_settings = self.get_device_settings()
        self._device_name = self._device_settings["name"]
        self._device_type = devtype
        self._device_firmware = firmware
        self._device_manufacturer = manufacturer \
            if manufacturer is not None \
            else MANUFACTURER_DICT[devtype]

        self._extra_state_attributes = {
            'sensor type': devtype,
            'uuid' if self.is_beacon else 'mac address': self._fkey
        }

        self._measurements = []
        self.rssi_values = []
        self.pending_update = False
        self.ready_for_update = False
        self._restore_state = self._device_settings["restore state"]
        self._err = None

        self._attr_name = f"{description.name} {self._device_name}"
        self._attr_unique_id = f"{description.unique_id}{self._device_name}"
        self._attr_should_poll = False
        self._attr_force_update = True
        self._attr_extra_state_attributes = self._extra_state_attributes

        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._fkey.upper())},
            "name": self._device_name,
            "model": devtype,
            "sw_version": firmware,
            "manufacturer": self._device_manufacturer,
        }

    async def async_added_to_hass(self):
        """Handle entity which will be added."""
        _LOGGER.debug("async_added_to_hass called for %s", self._attr_name)
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
            self._attr_native_unit_of_measurement = old_state.unit_of_measurement
        except AttributeError:
            pass
        self._state = old_state.state

        restore_attr = RESTORE_ATTRIBUTES
        restore_attr.append('mac address' if self.is_beacon else 'uuid')

        for attr in restore_attr:
            if attr in old_state.attributes:
                if attr in ['uuid', 'mac address']:
                    self._extra_state_attributes[attr] = identifier_normalize(old_state.attributes[attr])
                    continue

                self._extra_state_attributes[attr] = old_state.attributes[attr]
        self.ready_for_update = True

    @property
    def is_beacon(self):
        """Check if entity is beacon."""
        return self._type == CONF_UUID

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    def get_device_settings(self):
        """Set device settings."""
        device_settings = {}

        # initial setup of device settings equal to integration settings
        dev_name = self._key
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
                if self._fkey.upper() == dict_get_or(device).upper():
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
            "reset timer": dev_reset_timer,
        }
        _LOGGER.debug(
            "Sensor device with %s %s has the following settings. "
            "Name: %s. "
            "Temperature unit: %s. "
            "Decimals: %s. "
            "Use Median: %s. "
            "Restore state: %s. "
            "Reset Timer: %s",
            'uuid' if self.is_beacon else 'mac address',
            self._fkey,
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

    def __init__(self, config, key, devtype, firmware, description, manufacturer = None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, description, manufacturer)
        self._rdecimals = self._device_settings["decimals"]
        self._jagged = False
        self._use_median = self._device_settings["use median"]
        self._period_cnt = 0

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._period_cnt = period_cnt
        self._measurements.append(data[self.entity_description.key])
        self._extra_state_attributes["sensor type"] = data["type"]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )

        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    async def async_update(self):
        """Update sensor state and attributes."""
        textattr = ""
        # formaldehyde decimals workaround
        if self.entity_description == "formaldehyde":
            rdecimals = 3
        else:
            rdecimals = self._rdecimals
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
            self._extra_state_attributes[textattr] = len(measurements)
            self._extra_state_attributes["median"] = state_median
            self._extra_state_attributes["mean"] = state_mean
            if self.entity_description.key != "rssi":
                self._extra_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
            if self._period_cnt >= 1:
                self._measurements.clear()
                self.rssi_values.clear()
        except (AttributeError, AssertionError):
            _LOGGER.debug(
                "Sensor %s not yet ready for update", self.entity_description.name
            )
        except ZeroDivisionError as err:
            self._err = err
        except IndexError as err:
            self._err = err
        except RuntimeError as err:
            self._err = err
        if self._err:
            _LOGGER.error(
                "Sensor %s (%s) update error: %s",
                self.entity_description.name,
                self._device_type,
                self._err,
            )
        self.pending_update = False


class TemperatureSensor(MeasuringSensor):
    """Representation of a Temperature sensor."""

    def __init__(self, config, key, devtype, firmware, description, manufacturer = None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, description, manufacturer)
        self._attr_native_unit_of_measurement = self._device_settings["temperature unit"]

        if devtype in KETTLES:
            self._temp_min = CONF_TMIN_KETTLES
            self._temp_max = CONF_TMAX_KETTLES
        elif devtype in PROBES:
            self._temp_min = CONF_TMIN_PROBES
            self._temp_max = CONF_TMAX_PROBES
        else:
            self._temp_min = CONF_TMIN
            self._temp_max = CONF_TMAX
        self._lower_temp_limit = self.temperature_limit(config, key, self._temp_min)
        self._upper_temp_limit = self.temperature_limit(config, key, self._temp_max)
        self._log_spikes = config[CONF_LOG_SPIKES]

    def temperature_limit(self, config, key, temp):
        """Set limits for temperature measurement in °C or °F."""
        if config[CONF_DEVICES]:
            for device in config[CONF_DEVICES]:
                if self._fkey in dict_get_or(device).upper():
                    if CONF_TEMPERATURE_UNIT in device:
                        if device[CONF_TEMPERATURE_UNIT] == TEMP_FAHRENHEIT:
                            temp_fahrenheit = temp * 9 / 5 + 32
                            return temp_fahrenheit
                    break
        return temp

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._period_cnt = period_cnt
        if (
            not self._lower_temp_limit
            <= data[self.entity_description.key]
            <= self._upper_temp_limit
            and not self.is_beacon
        ):
            if self._log_spikes:
                _LOGGER.error(
                    "Temperature spike: %s (%s)",
                    data[self.entity_description.key],
                    self._key,
                )
            self.pending_update = False
            return
        self._measurements.append(data[self.entity_description.key])
        self._extra_state_attributes["sensor type"] = data["type"]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class HumiditySensor(MeasuringSensor):
    """Representation of a Humidity sensor."""

    def __init__(self, config, key, devtype, firmware, description, manufacturer = None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, description, manufacturer)
        self._log_spikes = config[CONF_LOG_SPIKES]
        # LYWSD03MMC / MHO-C401 "jagged" humidity workaround
        if devtype in ("LYWSD03MMC", "MHO-C401"):
            if self._device_firmware is not None:
                if self._device_firmware[0:6] == "Xiaomi":
                    self._jagged = True

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._period_cnt = period_cnt
        if (
            not CONF_HMIN
            <= data[self.entity_description.key]
            <= CONF_HMAX
            and not self.is_beacon
        ):
            if self._log_spikes:
                _LOGGER.error(
                    "Humidity spike: %s (%s)",
                    data[self.entity_description.key],
                    self._key,
                )
            self.pending_update = False
            return
        if self._jagged is True:
            self._measurements.append(int(data[self.entity_description.key]))
        else:
            self._measurements.append(data[self.entity_description.key])
        self._extra_state_attributes["sensor type"] = data["type"]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class BatterySensor(MeasuringSensor):
    """Representation of a Battery sensor."""

    def __init__(self, config, key, devtype, firmware, description, manufacturer = None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, description, manufacturer)

    def collect(self, data, period_cnt, batt_attr=None):
        """Battery measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._period_cnt = period_cnt
        self._state = data[self.entity_description.key]
        self._extra_state_attributes["sensor type"] = data["type"]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        self.pending_update = True

    async def async_update(self):
        """Update sensor state and attributes."""
        self._extra_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False


class InstantUpdateSensor(BaseSensor):
    """Base class for instant updating sensor entity."""

    def __init__(self, config, key, devtype, firmware, description, manufacturer = None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, description, manufacturer)
        self._reset_timer = self._device_settings["reset timer"]

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return

        if self.entity_description.key in ['uuid', 'mac']:
            data[self.entity_description.key] = identifier_normalize(data[self.entity_description.key])
        self._state = data[self.entity_description.key]

        self._extra_state_attributes["sensor type"] = data["type"]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    async def async_update(self):
        """Update sensor state and attributes."""
        self._extra_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False


class AccelerationSensor(InstantUpdateSensor):
    """Representation of a Acceleration sensor."""

    def __init__(self, config, key, devtype, firmware, description, manufacturer = None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, description, manufacturer)

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self.entity_description.key]
        self._extra_state_attributes["sensor type"] = data["type"]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes["acceleration x"] = data["acceleration x"]
        self._extra_state_attributes["acceleration y"] = data["acceleration y"]
        self._extra_state_attributes["acceleration z"] = data["acceleration z"]
        self._extra_state_attributes['mac address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class WeightSensor(InstantUpdateSensor):
    """Representation of a Weight sensor."""

    def __init__(self, config, key, devtype, firmware, description, manufacturer = None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, description, manufacturer)

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self.entity_description.key]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        if self.entity_description.key == "non-stabilized weight":
            self._extra_state_attributes["stabilized"] = bool(data["stabilized"])
            if "weight removed" in data:
                self._extra_state_attributes["weight removed"] = bool(
                    data["weight removed"]
                )
        if "impedance" in data:
            self._extra_state_attributes["impedance"] = data["impedance"]
        if "weight unit" in data:
            self._attr_native_unit_of_measurement = data["weight unit"]
        else:
            self._attr_native_unit_of_measurement = None
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class EnergySensor(InstantUpdateSensor):
    """Representation of an Energy sensor."""

    def __init__(self, config, key, devtype, firmware, description, manufacturer = None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, description, manufacturer)
        self._rdecimals = self._device_settings["decimals"]

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = round(data[self.entity_description.key], self._rdecimals)
        self._extra_state_attributes["sensor type"] = data["type"]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        if "energy unit" in data:
            self._attr_native_unit_of_measurement = data["energy unit"]
        else:
            self._attr_native_unit_of_measurement = (
                self.entity_description.native_unit_of_measurement
            )
        if "constant" in data:
            self._extra_state_attributes["constant"] = data["constant"]
        if "light level" in data:
            self._extra_state_attributes["light level"] = data["light level"]
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class PowerSensor(InstantUpdateSensor):
    """Representation of a Power sensor."""

    def __init__(self, config, key, devtype, firmware, description, manufacturer = None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, description, manufacturer)
        self._rdecimals = self._device_settings["decimals"]

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = round(data[self.entity_description.key], self._rdecimals)
        self._extra_state_attributes["sensor type"] = data["type"]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        if "power unit" in data:
            self._attr_native_unit_of_measurement = data["power unit"]
        else:
            self._attr_native_unit_of_measurement = (
                self.entity_description.native_unit_of_measurement
            )
        if "constant" in data:
            self._extra_state_attributes["constant"] = data["constant"]
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class ButtonSensor(InstantUpdateSensor):
    """Representation of a Button sensor."""

    def __init__(self, config, key, devtype, firmware, description, manufacturer = None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, description, manufacturer)

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurement collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self.entity_description.key]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    def reset_state(self, event=None):
        """Reset state of the sensor."""
        self._state = "no press"
        self.schedule_update_ha_state(False)

    async def async_update(self):
        """Update."""
        self._extra_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        if self._reset_timer > 0:
            _LOGGER.debug("Reset timer is set to: %i seconds", self._reset_timer)
            async_call_later(self.hass, self._reset_timer, self.reset_state)
        self.rssi_values.clear()
        self.pending_update = False


class DimmerSensor(InstantUpdateSensor):
    """Representation of a Dimmer sensor."""

    def __init__(self, config, key, devtype, firmware, description, manufacturer = None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, description, manufacturer)
        self._button = "button"
        self._dimmer = self.entity_description.key

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._button] + " " + str(data[self._dimmer]) + " steps"
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        self._extra_state_attributes["dimmer value"] = data[self._dimmer]
        self._extra_state_attributes["last type of press"] = data[self._button]
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    def reset_state(self, event=None):
        """Reset state of the sensor."""
        self._state = "no press"
        self.schedule_update_ha_state(False)

    async def async_update(self):
        """Update."""
        self._extra_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        if self._reset_timer > 0:
            _LOGGER.debug("Reset timer is set to: %i seconds", self._reset_timer)
            async_call_later(self.hass, self._reset_timer, self.reset_state)
        self.rssi_values.clear()
        self.pending_update = False


class SwitchSensor(InstantUpdateSensor):
    """Representation of a Switch sensor."""

    def __init__(self, config, key, devtype, firmware, description, manufacturer = None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, description, manufacturer)
        self._button_switch = "button switch"
        self._button = self.entity_description.key

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        if data[self._button] == "toggle":
            self._state = data[self._button_switch]
        else:
            self.pending_update = False
            return
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        self._extra_state_attributes["last press"] = self._state
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    def reset_state(self, event=None):
        """Reset state of the sensor."""
        self._state = "no press"
        self.schedule_update_ha_state(False)

    async def async_update(self):
        """Update."""
        self._extra_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        if self._reset_timer > 0:
            _LOGGER.debug("Reset timer is set to: %i seconds", self._reset_timer)
            async_call_later(self.hass, self._reset_timer, self.reset_state)
        self.rssi_values.clear()
        self.pending_update = False


class BaseRemoteSensor(InstantUpdateSensor):
    """Representation of a Remote sensor."""

    def __init__(self, config, key, devtype, firmware, description, manufacturer = None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, description, manufacturer)
        self._button = "button"
        self._remote = self.entity_description.key

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._button] + " " + data[self._remote]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        self._extra_state_attributes["last remote button pressed"] = data[self._remote]
        self._extra_state_attributes["last type of press"] = data["button"]
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    def reset_state(self, event=None):
        """Reset state of the sensor."""
        self._state = "no press"
        self.schedule_update_ha_state(False)

    async def async_update(self):
        """Update."""
        self._extra_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        if self._reset_timer > 0:
            _LOGGER.debug("Reset timer is set to: %i seconds", self._reset_timer)
            async_call_later(self.hass, self._reset_timer, self.reset_state)
        self.rssi_values.clear()
        self.pending_update = False


class VolumeDispensedSensor(InstantUpdateSensor):
    """Representation of a Kegtron Volume dispensed sensor."""

    def __init__(self, config, key, devtype, firmware, description, manufacturer = None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, description, manufacturer)

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self.entity_description.key]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        self._extra_state_attributes["volume start"] = data["volume start"]
        self._extra_state_attributes["keg size"] = data["keg size"]
        self._extra_state_attributes["port name"] = data["port name"]
        self._extra_state_attributes["port state"] = data["port state"]
        self._extra_state_attributes["port index"] = data["port index"]
        self.pending_update = True
