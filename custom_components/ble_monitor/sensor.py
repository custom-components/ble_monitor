"""Passive BLE monitor sensor platform."""
import asyncio
import logging
import statistics as sts
from datetime import timedelta

from homeassistant.components.sensor import RestoreSensor, SensorEntity
from homeassistant.const import (ATTR_BATTERY_LEVEL, CONF_DEVICES, CONF_MAC,
                                 CONF_NAME, CONF_TEMPERATURE_UNIT,
                                 CONF_UNIQUE_ID, UnitOfMass, UnitOfTemperature)
from homeassistant.helpers import device_registry, entity_registry
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.typing import StateType
from homeassistant.util import dt
from homeassistant.util.unit_conversion import TemperatureConverter

from .const import (AUTO_MANUFACTURER_DICT, AUTO_SENSOR_LIST,
                    CONF_DEVICE_RESET_TIMER, CONF_DEVICE_RESTORE_STATE,
                    CONF_DEVICE_USE_MEDIAN, CONF_HMAX, CONF_HMIN,
                    CONF_LOG_SPIKES, CONF_PERIOD, CONF_RESTORE_STATE,
                    CONF_TMAX, CONF_TMAX_KETTLES, CONF_TMAX_PROBES, CONF_TMIN,
                    CONF_TMIN_KETTLES, CONF_TMIN_PROBES, CONF_USE_MEDIAN,
                    CONF_UUID, DEFAULT_DEVICE_RESET_TIMER, DOMAIN, KETTLES,
                    MANUFACTURER_DICT, MEASUREMENT_DICT, PROBES,
                    RENAMED_FIRMWARE_DICT, RENAMED_MANUFACTURER_DICT,
                    RENAMED_MODEL_DICT, SENSOR_TYPES,
                    BLEMonitorSensorEntityDescription)
from .helper import (detect_conf_type, dict_get_or, dict_get_or_normalize,
                     identifier_clean, identifier_normalize)

_LOGGER = logging.getLogger(__name__)

RESTORE_ATTRIBUTES = [
    "median",
    "mean",
    "last_median_of",
    "last_mean_of",
    "rssi",
    "firmware",
    "last_packet_id",
    "last_button_press",
    "last_remote_button_pressed",
    "last_type_o_press",
    "dimmer_value",
    "constant",
    "volume_start",
    "keg_size",
    "port_name",
    "port_state",
    "port_index",
    "impedance",
    "acceleration_x",
    "acceleration_y",
    "acceleration_z",
    "light_level",
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

        async def async_add_sensor(key, device_model, firmware, auto_sensors, manufacturer=None):
            if device_model in AUTO_MANUFACTURER_DICT:
                sensors = {}
                for measurement in auto_sensors:
                    if key not in sensors_by_key:
                        sensors_by_key[key] = {}
                    if measurement not in sensors_by_key[key]:
                        entity_description = [item for item in SENSOR_TYPES if item.key is measurement][0]
                        sensors[measurement] = globals()[entity_description.sensor_class](
                            self.config, key, device_model, firmware, entity_description, manufacturer
                        )
                        self.add_entities([sensors[measurement]])
                        sensors_by_key[key].update(sensors)
                    else:
                        sensors = sensors_by_key[key]
            else:
                averaging_sensors = MEASUREMENT_DICT[device_model][0]
                instant_sensors = MEASUREMENT_DICT[device_model][1]
                device_sensors = averaging_sensors + instant_sensors
                if key not in sensors_by_key:
                    sensors = {}
                    sensors_by_key[key] = {}
                    for measurement in device_sensors:
                        entity_description = [item for item in SENSOR_TYPES if item.key is measurement][0]
                        sensors[measurement] = globals()[entity_description.sensor_class](
                            self.config, key, device_model, firmware, entity_description, manufacturer
                        )
                        self.add_entities([sensors[measurement]])
                    sensors_by_key[key].update(sensors)
                else:
                    sensors = sensors_by_key[key]
            return sensors

        _LOGGER.debug("Entities updater loop started!")
        sensors_by_key = {}
        sensors = {}
        batt = {}  # batteries
        batt_cgpr1 = []
        rssi = {}  # rssi
        ble_adv_cnt = 0

        ts_now = dt.now()
        ts_restart = ts_now
        ts_last_update = ts_now
        period_cnt = 0

        data = {}
        await asyncio.sleep(0)

        # setup sensors of configured devices on startup when device model is available in registry
        if self.config[CONF_DEVICES]:
            dev_registry = device_registry.async_get(hass)
            ent_registry = entity_registry.async_get(hass)
            for device in self.config[CONF_DEVICES]:
                # get device_model and firmware from device registry to setup sensor
                key = dict_get_or(device)
                dev = dev_registry.async_get_device({(DOMAIN, key.upper())}, set())
                auto_sensors = set()
                if dev:
                    key = identifier_clean(key)
                    device_id = dev.id
                    device_model = dev.model
                    firmware = dev.sw_version
                    manufacturer = dev.manufacturer
                    # migrate to new model/firmware/manufacturer if changed
                    device_model = RENAMED_MODEL_DICT.get(device_model, device_model)
                    firmware = RENAMED_FIRMWARE_DICT.get(firmware, firmware)
                    manufacturer = RENAMED_MANUFACTURER_DICT.get(manufacturer, manufacturer)
                    # get all entities for this device
                    entity_list = entity_registry.async_entries_for_device(
                        registry=ent_registry, device_id=device_id, include_disabled_entities=False
                    )
                    # find the measurement key for each entity
                    for entity in entity_list:
                        unique_id_prefix = (entity.unique_id).removesuffix(key).removesuffix(dev.name)

                        for sensor_type in SENSOR_TYPES:
                            if sensor_type.unique_id == unique_id_prefix:
                                sensor_key = sensor_type.key
                                auto_sensors.add(sensor_key)

                    if device_model and firmware and auto_sensors:
                        sensors = await async_add_sensor(
                            key, device_model, firmware, auto_sensors, manufacturer
                        )
                    else:
                        continue
                else:
                    pass
        else:
            sensors = {}

        # Set up new sensors when first BLE advertisement is received
        sensors = {}
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
                key = identifier_clean(dict_get_or(data))
                # the RSSI value will be averaged for all valuable packets
                if key not in rssi:
                    rssi[key] = []
                rssi[key].append(int(data["rssi"]))
                batt_attr = None
                device_model = data["type"]
                firmware = data["firmware"]
                manufacturer = data["manufacturer"] if "manufacturer" in data else None
                # migrate to new model/firmware/manufacturer if changed
                device_model = RENAMED_MODEL_DICT.get(device_model, device_model)
                firmware = RENAMED_FIRMWARE_DICT.get(firmware, firmware)
                manufacturer = RENAMED_MANUFACTURER_DICT.get(manufacturer, manufacturer)
                auto_sensors = set()
                if device_model in AUTO_MANUFACTURER_DICT:
                    for measurement in AUTO_SENSOR_LIST:
                        if measurement in data:
                            auto_sensors.add(measurement)
                sensors = await async_add_sensor(
                    key, device_model, firmware, auto_sensors, manufacturer
                )
                device_sensors = sensors.keys()

                if data["data"] is False:
                    data = None
                    continue

                # battery attribute
                if "battery" in device_sensors:
                    if "battery" in data:
                        if device_model == "CGPR1" and firmware[0:6] == "Xiaomi":
                            # Workaround to remove the "counter" value in battery advertisements for CGPR1
                            old_data = batt_cgpr1.copy()
                            batt_cgpr1.append(data["battery"])
                            if len(batt_cgpr1) > 5:
                                batt_cgpr1.pop(0)
                            if data["battery"] in old_data:
                                batt[key] = int(data["battery"])
                                batt_attr = batt[key]
                            else:
                                data.pop("battery")
                                try:
                                    batt_attr = batt[key]
                                except KeyError:
                                    batt_attr = None
                        else:
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
                        entity = sensors[measurement]
                        if device_model in AUTO_MANUFACTURER_DICT:
                            if entity.update_behavior in ["Instantly", "StateChange"]:
                                instant_sensors = [measurement]
                            else:
                                instant_sensors = []
                        else:
                            instant_sensors = MEASUREMENT_DICT[device_model][1]
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
            ts_now = dt.now()
            if ts_now - ts_last_update < timedelta(seconds=self.period):
                continue
            ts_last_update = ts_now
            period_cnt += 1
            # restarting scanner
            self.monitor.restart()
            # updating the state for every updated measuring device
            for key, edict in sensors_by_key.items():
                for entity in edict.values():
                    if entity.pending_update is True:
                        if entity.ready_for_update is True:
                            entity.rssi_values = rssi[key].copy()
                            entity.async_schedule_update_ha_state(True)
            for key in rssi:
                rssi[key].clear()

            _LOGGER.debug(
                "%i BLE advertisements processed for %i sensor device(s)",
                ble_adv_cnt,
                len(sensors_by_key),
            )
            ble_adv_cnt = 0


class BaseSensor(RestoreSensor, SensorEntity):
    """Base class for all sensor entities."""

    # BaseSensor (Class)
    # |--MeasuringSensor (Class)
    # |  |--TemperatureSensor (Class)
    # |  |  |**temperature
    # |  |  |**temperature probe 1 till 6
    # |  |  |**temperature probe tip
    # |  |  |**temperature alarm 1 till 4
    # |  |  |**low temperature alarm 1 till 4
    # |  |  |**meat temperature
    # |  |  |**ambient temperature
    # |  |--HumiditySensor (Class)
    # |  |  |**humidity
    # |  |**moisture
    # |  |**pressure
    # |  |**water pressure
    # |  |**conductivity
    # |  |**illuminance
    # |  |**formaldehyde
    # |  |**dewpoint
    # |  |**rssi
    # |  |--BatterySensor (Class)
    # |  |  |**battery
    # |  |**voltage
    # |  |**CO2
    # |  |**PM2.5
    # |  |**PM10
    # |  |**gravity
    # |  |**TVOC
    # |  |**Air Quality Index
    # |  |**UV index
    # |  |**volume
    # |  |**volume mL
    # |  |**volume flow rate
    # |  |**flow
    # |  |**gas
    # |  |**water
    # |  |**fresh/grey/black/lpg/galley/chemical tank
    # |--InstantUpdateSensor (Class)
    # |  |**consumable
    # |  |**heart rate
    # |  |**opening percentage
    # |  |**pulse
    # |  |**shake
    # |  |**rotation
    # |  |**roll
    # |  |**pitch
    # |  |**distance
    # |  |**distance mm
    # |  |**duration
    # |  |**pressure present duration
    # |  |**pressure not present duration
    # |  |**pressure present time set
    # |  |**pressure present not time set
    # |  |**current
    # |  |**speed
    # |  |**gyroscope
    # |  |**MagneticFieldSensor
    # |  |**MagneticFieldDirectionSensor
    # |  |**impedance
    # |  |**impedance low
    # |  |**profile id
    # |  |--StateChangedSensor (Class)
    # |  |  |**mac
    # |  |  |**uuid
    # |  |  |**major
    # |  |  |**minor
    # |  |  |**count
    # |  |  |**movement counter
    # |  |  |**score
    # |  |  |**air quality
    # |  |  |**text
    # |  |  |**pump mode
    # |  |  |**timestamp
    # |  |--OilBurnerStateSensor (Class)
    # |  |  |**burner_state
    # |  |  |**burner_last_end_cause
    # |  |  |**burner_cycle_count
    # |  |--AccelerationSensor (Class)
    # |  |  |**acceleration
    # |  |--WeightSensor (Class)
    # |  |  |**weight
    # |  |  |**stabilized weight
    # |  |  |**non-stabilized weight
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
    # |  |  |**four btn switch 1
    # |  |  |**four btn switch 2
    # |  |  |**four btn switch 3
    # |  |  |**four btn switch 4
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
        entity_description: BLEMonitorSensorEntityDescription,
        manufacturer=None,
    ) -> None:
        """Initialize the sensor."""
        self.entity_description = entity_description
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
            else MANUFACTURER_DICT.get(
                devtype,
                AUTO_MANUFACTURER_DICT.get(devtype, None)
            )

        self._extra_state_attributes = {
            'sensor_type': devtype,
            'uuid' if self.is_beacon else 'mac_address': self._fkey
        }

        self._measurements = []
        self.rssi_values = []
        self.update_behavior = self.entity_description.update_behavior
        self.pending_update = False
        self.ready_for_update = False
        self._restore_state = self._device_settings["restore_state"]
        self._err = None

        self._attr_name = f"{self.entity_description.name} {self._device_name}"
        self._attr_unique_id = f"{self.entity_description.unique_id}{self._device_name}"
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

        if self._restore_state is False:
            self.ready_for_update = True
            return
        # Retrieve the old state and unit of measumrement from the registry
        last_sensor_data = await self.async_get_last_sensor_data()

        if not last_sensor_data:
            self.ready_for_update = True
            return

        last_native_value = last_sensor_data.native_value
        last_native_unit_of_measurement = last_sensor_data.native_unit_of_measurement

        if last_native_value is None:
            self.ready_for_update = True
            return

        # Restore the old state and unit of measurement
        try:
            if last_native_unit_of_measurement in [
                UnitOfTemperature.CELSIUS, UnitOfTemperature.FAHRENHEIT
            ]:
                # Convert old state temperature to a temperature in the device setting temperature unit
                self._attr_native_unit_of_measurement = self._device_settings["temperature unit"]
                if last_native_value:
                    self._state = TemperatureConverter.convert(
                        value=float(last_native_value),
                        from_unit=last_native_unit_of_measurement,
                        to_unit=self._device_settings["temperature unit"],
                    )
                else:
                    self._state = last_native_value
            else:
                self._attr_native_unit_of_measurement = last_native_unit_of_measurement
                self._state = last_native_value
        except (KeyError, ValueError):
            self._state = last_native_value

        # Restore the old attributes
        last_state = await self.async_get_last_state()
        restore_attr = RESTORE_ATTRIBUTES
        restore_attr.append('mac_address' if self.is_beacon else 'uuid')

        for attr in restore_attr:
            if attr in last_state.attributes:
                if attr in ['uuid', 'mac_address']:
                    self._extra_state_attributes[attr] = identifier_normalize(
                        last_state.attributes[attr]
                    )
                    continue

                self._extra_state_attributes[attr] = last_state.attributes[attr]
        self.ready_for_update = True

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        if self.entity_description.key in ['battery']:
            if self._device_type == "HHCCJCY01":
                return False

        if not self.is_beacon:
            return True

        if self.entity_description.key in [
            'cypress temperature', 'cypress humidity', 'uuid', 'pressure present duration',
            'pressure not present duration', 'pressure present time set', 'pressure not present time set'
        ]:
            return False

        return True

    @property
    def is_beacon(self):
        """Check if entity is beacon."""
        return self._type == CONF_UUID

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self._state  # type: ignore[no-any-return]

    def get_device_settings(self):
        """Set device settings."""
        device_settings = {}

        # initial setup of device settings equal to integration settings
        dev_name = self._key
        dev_temperature_unit = UnitOfTemperature.CELSIUS
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
            "use median": dev_use_median,
            "restore_state": dev_restore_state,
            "reset_timer": dev_reset_timer,
        }
        _LOGGER.debug(
            "Sensor device with %s %s has the following settings. "
            "Name: %s. "
            "Temperature unit: %s. "
            "Use Median: %s. "
            "Restore state: %s. "
            "Reset Timer: %s",
            'uuid' if self.is_beacon else 'mac_address',
            self._fkey,
            device_settings["name"],
            device_settings["temperature unit"],
            device_settings["use median"],
            device_settings["restore_state"],
            device_settings["reset_timer"],
        )
        return device_settings


class MeasuringSensor(BaseSensor):
    """Base class for measuring sensor entities."""

    def __init__(self, config, key, devtype, firmware, entity_description, manufacturer=None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, entity_description, manufacturer)
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
        self._extra_state_attributes["sensor_type"] = data["type"]
        self._extra_state_attributes["last_packet_id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac_address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )

        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    async def async_update(self):
        """Update sensor state and attributes."""
        textattr = ""
        try:
            measurements = self._measurements
            state_median = sts.median(measurements)
            state_mean = sts.mean(measurements)
            if self._use_median:
                textattr = "last_median_of"
                self._state = state_median
            else:
                textattr = "last_mean_of"
                self._state = state_mean
            self._extra_state_attributes[textattr] = len(measurements)
            self._extra_state_attributes["median"] = state_median
            self._extra_state_attributes["mean"] = state_mean
            if self.entity_description.key != "rssi":
                if self.rssi_values:
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

    def __init__(self, config, key, devtype, firmware, entity_description, manufacturer=None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, entity_description, manufacturer)
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
        self._lower_temp_limit = self.temperature_limit(config, self._temp_min)
        self._upper_temp_limit = self.temperature_limit(config, self._temp_max)
        self._log_spikes = config[CONF_LOG_SPIKES]

    def temperature_limit(self, config, temp):
        """Set limits for temperature measurement in °C or °F."""
        if config[CONF_DEVICES]:
            for device in config[CONF_DEVICES]:
                if self._fkey in dict_get_or(device).upper():
                    if CONF_TEMPERATURE_UNIT in device:
                        if device[CONF_TEMPERATURE_UNIT] == UnitOfTemperature.FAHRENHEIT:
                            temp_fahrenheit = TemperatureConverter.convert(
                                value=temp,
                                from_unit=UnitOfTemperature.CELSIUS,
                                to_unit=UnitOfTemperature.FAHRENHEIT
                            )
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
        self._extra_state_attributes["sensor_type"] = data["type"]
        self._extra_state_attributes["last_packet_id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac_address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class HumiditySensor(MeasuringSensor):
    """Representation of a Humidity sensor."""

    def __init__(self, config, key, devtype, firmware, entity_description, manufacturer=None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, entity_description, manufacturer)
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
        self._extra_state_attributes["sensor_type"] = data["type"]
        self._extra_state_attributes["last_packet_id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac_address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class BatterySensor(MeasuringSensor):
    """Representation of a Battery sensor."""

    def __init__(self, config, key, devtype, firmware, entity_description, manufacturer=None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, entity_description, manufacturer)

    def collect(self, data, period_cnt, batt_attr=None):
        """Battery measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._period_cnt = period_cnt
        self._state = data[self.entity_description.key]
        self._extra_state_attributes["sensor_type"] = data["type"]
        self._extra_state_attributes["last_packet_id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac_address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        self.pending_update = True

    async def async_update(self):
        """Update sensor state and attributes."""
        if self.rssi_values:
            self._extra_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False


class InstantUpdateSensor(BaseSensor):
    """Base class for instant updating sensor entity."""

    def __init__(self, config, key, devtype, firmware, entity_description, manufacturer=None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, entity_description, manufacturer)
        self._reset_timer = self._device_settings["reset_timer"]

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return

        if self.entity_description.key in ['uuid', 'mac']:
            data[self.entity_description.key] = identifier_normalize(data[self.entity_description.key])
        self._state = data[self.entity_description.key]

        self._extra_state_attributes["sensor_type"] = data["type"]
        self._extra_state_attributes["last_packet_id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac_address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    async def async_update(self):
        """Update sensor state and attributes."""
        if self.rssi_values:
            self._extra_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False


class StateChangedSensor(InstantUpdateSensor):
    """Representation of a State changed sensor."""

    def __init__(self, config, key, devtype, firmware, entity_description, manufacturer=None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, entity_description, manufacturer)

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        state = self._state
        if state and self.entity_description.key == CONF_UUID:
            state = identifier_clean(state)

        if self.enabled is False or state == data[self.entity_description.key]:
            self.pending_update = False
            return
        if "pump id" in data:
            self._extra_state_attributes["pump_id"] = data["pump id"]
        if "battery status" in data:
            self._extra_state_attributes["battery_status"] = data["battery status"]
        super().collect(data, period_cnt, batt_attr)

class OilBurnerStateSensor(InstantUpdateSensor):
    """Representation of a State changed sensor."""

    def __init__(self, config, key, devtype, firmware, entity_description, manufacturer=None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, entity_description, manufacturer)

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        state = self._state
        if state and self.entity_description.key == CONF_UUID:
            state = identifier_clean(state)

        if self.enabled is False or state == data[self.entity_description.key]:
            self.pending_update = False
            return
        if "burner_state" in data:
            self._extra_state_attributes["burner_state"] = data["burner_state"]
        if "burner_last_end_cause" in data:
            self._extra_state_attributes["burner_last_end_cause"] = data["burner_last_end_cause"]
        if "burner_cycle_count" in data:
            self._extra_state_attributes["burner_cycle_count"] = data["burner_cycle_count"]
        super().collect(data, period_cnt, batt_attr)

class AccelerationSensor(InstantUpdateSensor):
    """Representation of a Acceleration sensor."""

    def __init__(self, config, key, devtype, firmware, entity_description, manufacturer=None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, entity_description, manufacturer)

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self.entity_description.key]
        self._extra_state_attributes["sensor_type"] = data["type"]
        self._extra_state_attributes["last_packet_id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        if "acceleration x" in data:
            self._extra_state_attributes["acceleration_x"] = data["acceleration x"]
            self._extra_state_attributes["acceleration_y"] = data["acceleration y"]
            self._extra_state_attributes["acceleration_z"] = data["acceleration z"]
        self._extra_state_attributes['mac_address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class WeightSensor(InstantUpdateSensor):
    """Representation of a Weight sensor."""

    def __init__(self, config, key, devtype, firmware, entity_description, manufacturer=None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, entity_description, manufacturer)

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self.entity_description.key]
        self._extra_state_attributes["last_packet_id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac_address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        if self.entity_description.key == "non-stabilized weight":
            self._extra_state_attributes["stabilized"] = bool(data["stabilized"])
            if "weight removed" in data:
                self._extra_state_attributes["weight removed"] = bool(
                    data["weight removed"]
                )
                if "impedance" not in data and data["type"] == "Mi Scale V2" and data["weight removed"] == 0:
                    self._extra_state_attributes["impedance"] = "unavailable"
        if "impedance" in data:
            self._extra_state_attributes["impedance"] = data["impedance"]
        if "weight unit" in data:
            self._attr_native_unit_of_measurement = data["weight unit"]
        else:
            self._attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class EnergySensor(InstantUpdateSensor):
    """Representation of an Energy sensor."""

    def __init__(self, config, key, devtype, firmware, entity_description, manufacturer=None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, entity_description, manufacturer)

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self.entity_description.key]
        self._extra_state_attributes["sensor_type"] = data["type"]
        self._extra_state_attributes["last_packet_id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac_address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
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
            self._extra_state_attributes["light_level"] = data["light level"]
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class PowerSensor(InstantUpdateSensor):
    """Representation of a Power sensor."""

    def __init__(self, config, key, devtype, firmware, entity_description, manufacturer=None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, entity_description, manufacturer)

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self.entity_description.key]
        self._extra_state_attributes["sensor_type"] = data["type"]
        self._extra_state_attributes["last_packet_id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac_address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
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

    def __init__(self, config, key, devtype, firmware, entity_description, manufacturer=None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, entity_description, manufacturer)

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurement collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self.entity_description.key]
        self._extra_state_attributes["last_packet_id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac_address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
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
        if self.rssi_values:
            self._extra_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        if self._reset_timer > 0:
            _LOGGER.debug("Reset timer is set to: %i seconds", self._reset_timer)
            async_call_later(self.hass, self._reset_timer, self.reset_state)
        self.rssi_values.clear()
        self.pending_update = False


class DimmerSensor(InstantUpdateSensor):
    """Representation of a Dimmer sensor."""

    def __init__(self, config, key, devtype, firmware, entity_description, manufacturer=None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, entity_description, manufacturer)
        self._dimmer = self.entity_description.key
        self._steps = "steps"

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._dimmer] + " " + str(data[self._steps]) + " steps"
        self._extra_state_attributes["last_packet_id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac_address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        self._extra_state_attributes["dimmer_value"] = data[self._steps]
        self._extra_state_attributes["last_type_of_press"] = data[self._dimmer]
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    def reset_state(self, event=None):
        """Reset state of the sensor."""
        self._state = "no press"
        self.schedule_update_ha_state(False)

    async def async_update(self):
        """Update."""
        if self.rssi_values:
            self._extra_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        if self._reset_timer > 0:
            _LOGGER.debug("Reset timer is set to: %i seconds", self._reset_timer)
            async_call_later(self.hass, self._reset_timer, self.reset_state)
        self.rssi_values.clear()
        self.pending_update = False


class SwitchSensor(InstantUpdateSensor):
    """Representation of a Switch sensor."""

    def __init__(self, config, key, devtype, firmware, entity_description, manufacturer=None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, entity_description, manufacturer)
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
        self._extra_state_attributes["last_packet_id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac_address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        self._extra_state_attributes["last_press"] = self._state
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    def reset_state(self, event=None):
        """Reset state of the sensor."""
        self._state = "no press"
        self.schedule_update_ha_state(False)

    async def async_update(self):
        """Update."""
        if self.rssi_values:
            self._extra_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        if self._reset_timer > 0:
            _LOGGER.debug("Reset timer is set to: %i seconds", self._reset_timer)
            async_call_later(self.hass, self._reset_timer, self.reset_state)
        self.rssi_values.clear()
        self.pending_update = False


class BaseRemoteSensor(InstantUpdateSensor):
    """Representation of a Remote sensor."""

    def __init__(self, config, key, devtype, firmware, entity_description, manufacturer=None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, entity_description, manufacturer)
        self._button = "button"
        self._remote = self.entity_description.key

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._button] + " " + data[self._remote]
        self._extra_state_attributes["last_packet_id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac_address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        self._extra_state_attributes["last_remote_button_pressed"] = data[self._remote]
        self._extra_state_attributes["last_type_of_press"] = data["button"]
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    def reset_state(self, event=None):
        """Reset state of the sensor."""
        self._state = "no press"
        self.schedule_update_ha_state(False)

    async def async_update(self):
        """Update."""
        if self.rssi_values:
            self._extra_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        if self._reset_timer > 0:
            _LOGGER.debug("Reset timer is set to: %i seconds", self._reset_timer)
            async_call_later(self.hass, self._reset_timer, self.reset_state)
        self.rssi_values.clear()
        self.pending_update = False


class VolumeDispensedSensor(InstantUpdateSensor):
    """Representation of a Kegtron Volume dispensed sensor."""

    def __init__(self, config, key, devtype, firmware, entity_description, manufacturer=None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, entity_description, manufacturer)

    def collect(self, data, period_cnt, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self.entity_description.key]
        self._extra_state_attributes["last_packet_id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac_address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )
        self._extra_state_attributes["volume_start"] = data["volume start"]
        self._extra_state_attributes["keg_size"] = data["keg size"]
        self._extra_state_attributes["port_name"] = data["port name"]
        self._extra_state_attributes["port_state"] = data["port state"]
        self._extra_state_attributes["port_index"] = data["port index"]
        self.pending_update = True
