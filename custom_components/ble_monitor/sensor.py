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
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)

from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.components.sensor import SensorEntity
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
    RENAMED_MODEL_DICT,
    DOMAIN,
    SENSOR_TYPES,
    BLEMonitorSensorEntityDescription,
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

        async def async_add_sensor(mac, sensortype, firmware):
            averaging_sensors = MEASUREMENT_DICT[sensortype][0]
            instant_sensors = MEASUREMENT_DICT[sensortype][1]
            device_sensors = averaging_sensors + instant_sensors
            if mac not in sensors_by_mac:
                sensors = []
                for sensor in device_sensors:
                    description = [item for item in SENSOR_TYPES if item.key is sensor][
                        0
                    ]
                    sensors.insert(
                        device_sensors.index(sensor),
                        globals()[description.sensor_class](
                            self.config, mac, sensortype, firmware, description
                        ),
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
        rssi = {}  # rssi
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
                        if (
                            measurement in instant_sensors
                            or ts_now - ts_start < timedelta(seconds=self.period)
                        ):
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
                "%i BLE ADV messages processed for %i measuring device(s)",
                ble_adv_cnt,
                len(sensors_by_mac),
            )
            ble_adv_cnt = 0


class BaseSensor(RestoreEntity, SensorEntity):
    """Base class for all sensor entities."""

    # BaseSensor (Class)
    # |--MeasuringSensor (Class)
    # |  |--TemperatureSensor (Class)
    # |  |  |**temperature
    # |  |  |**temperature outdoor
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
        mac: str,
        devtype: str,
        firmware: str,
        description: BLEMonitorSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        self._config = config
        self._mac = mac
        self._fmac = ":".join(mac[i : i + 2] for i in range(0, len(mac), 2))
        self._state = None

        self._device_settings = self.get_device_settings()
        self._device_name = self._device_settings["name"]
        self._device_type = devtype
        self._device_firmware = firmware
        self._device_manufacturer = MANUFACTURER_DICT[devtype]
        self._extra_state_attributes = {}
        self._extra_state_attributes["sensor type"] = devtype
        self._extra_state_attributes["mac address"] = self._fmac
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
            "identifiers": {(DOMAIN, self._extra_state_attributes["mac address"])},
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
        if "median" in old_state.attributes:
            self._extra_state_attributes["median"] = old_state.attributes["median"]
        if "mean" in old_state.attributes:
            self._extra_state_attributes["mean"] = old_state.attributes["mean"]
        if "last median of" in old_state.attributes:
            self._extra_state_attributes["last median of"] = old_state.attributes[
                "last median of"
            ]
            self._state = old_state.attributes["median"]
        if "last mean of" in old_state.attributes:
            self._extra_state_attributes["last mean of"] = old_state.attributes[
                "last mean of"
            ]
            self._state = old_state.attributes["mean"]
        if "rssi" in old_state.attributes:
            self._extra_state_attributes["rssi"] = old_state.attributes["rssi"]
        if "firmware" in old_state.attributes:
            self._extra_state_attributes["firmware"] = old_state.attributes["firmware"]
        if "last packet id" in old_state.attributes:
            self._extra_state_attributes["last packet id"] = old_state.attributes[
                "last packet id"
            ]
        if "last button press" in old_state.attributes:
            self._extra_state_attributes["last button press"] = old_state.attributes[
                "last button press"
            ]
        if "last remote button pressed" in old_state.attributes:
            self._extra_state_attributes[
                "last remote button pressed"
            ] = old_state.attributes["last remote button pressed"]
        if "last type of press" in old_state.attributes:
            self._extra_state_attributes["last type of press"] = old_state.attributes[
                "last type of press"
            ]
        if "dimmer value" in old_state.attributes:
            self._extra_state_attributes["dimmer value"] = old_state.attributes[
                "dimmer value"
            ]
        if "constant" in old_state.attributes:
            self._extra_state_attributes["constant"] = old_state.attributes["constant"]
        if ATTR_BATTERY_LEVEL in old_state.attributes:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = old_state.attributes[
                ATTR_BATTERY_LEVEL
            ]
        self.ready_for_update = True

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

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
            "reset timer": dev_reset_timer,
        }
        _LOGGER.debug(
            "Sensor device with mac address %s has the following settings. "
            "Name: %s. "
            "Temperature unit: %s. "
            "Decimals: %s. "
            "Use Median: %s. "
            "Restore state: %s. "
            "Reset Timer: %s",
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

    def __init__(self, config, mac, devtype, firmware, description):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware, description)
        self._rdecimals = self._device_settings["decimals"]
        self._jagged = False
        self._use_median = self._device_settings["use median"]

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._measurements.append(data[self.entity_description.key])
        self._extra_state_attributes["sensor type"] = data["type"]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
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
            self._measurements.clear()
            self._extra_state_attributes["median"] = state_median
            self._extra_state_attributes["mean"] = state_mean
            if self.entity_description.key != "rssi":
                self._extra_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
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

    def __init__(self, config, mac, devtype, firmware, description):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware, description)
        self._attr_native_unit_of_measurement = self._device_settings["temperature unit"]

        self._temp_min = CONF_TMIN_KETTLES if devtype in KETTLES else CONF_TMIN
        self._temp_max = CONF_TMAX_KETTLES if devtype in KETTLES else CONF_TMAX
        self._lower_temp_limit = self.temperature_limit(config, mac, self._temp_min)
        self._upper_temp_limit = self.temperature_limit(config, mac, self._temp_max)
        self._log_spikes = config[CONF_LOG_SPIKES]

    def temperature_limit(self, config, mac, temp):
        """Set limits for temperature measurement in °C or °F."""
        fmac = ":".join(mac[i : i + 2] for i in range(0, len(mac), 2))
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
        if (
            not self._lower_temp_limit
            <= data[self.entity_description.key]
            <= self._upper_temp_limit
        ):
            if self._log_spikes:
                _LOGGER.error(
                    "Temperature spike: %s (%s)",
                    data[self.entity_description.key],
                    self._mac,
                )
            self.pending_update = False
            return
        self._measurements.append(data[self.entity_description.key])
        self._extra_state_attributes["sensor type"] = data["type"]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class HumiditySensor(MeasuringSensor):
    """Representation of a Humidity sensor."""

    def __init__(self, config, mac, devtype, firmware, description):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware, description)
        self._log_spikes = config[CONF_LOG_SPIKES]
        # LYWSD03MMC / MHO-C401 "jagged" humidity workaround
        if devtype in ("LYWSD03MMC", "MHO-C401"):
            if self._device_firmware is not None:
                if self._device_firmware[0:6] == "Xiaomi":
                    self._jagged = True

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        if not CONF_HMIN <= data[self.entity_description.key] <= CONF_HMAX:
            if self._log_spikes:
                _LOGGER.error(
                    "Humidity spike: %s (%s)",
                    data[self.entity_description.key],
                    self._mac,
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
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class BatterySensor(MeasuringSensor):
    """Representation of a Battery sensor."""

    def __init__(self, config, mac, devtype, firmware, description):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware, description)

    def collect(self, data, batt_attr=None):
        """Battery measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self.entity_description.key]
        self._extra_state_attributes["sensor type"] = data["type"]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self.pending_update = True

    async def async_update(self):
        """Update sensor state and attributes."""
        self._extra_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False


class InstantUpdateSensor(BaseSensor):
    """Base class for instant updating sensor entity."""

    def __init__(self, config, mac, devtype, firmware, description):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware, description)
        self._reset_timer = self._device_settings["reset timer"]

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self.entity_description.key]
        self._extra_state_attributes["sensor type"] = data["type"]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
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

    def __init__(self, config, mac, devtype, firmware, description):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware, description)

    def collect(self, data, batt_attr=None):
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
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class WeightSensor(InstantUpdateSensor):
    """Representation of a non-stabilized Weight sensor."""

    def __init__(self, config, mac, devtype, firmware, description):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware, description)

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self.entity_description.key]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        if self.entity_description.key == "non-stabilized weight":
            self._extra_state_attributes["stabilized"] = bool(data["stabilized"])
            self._extra_state_attributes["weight removed"] = bool(
                data["weight removed"]
            )
        if "weight unit" in data:
            self._attr_native_unit_of_measurement = data["weight unit"]
        else:
            self._attr_native_unit_of_measurement = None
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True


class EnergySensor(InstantUpdateSensor):
    """Representation of an Energy sensor."""

    def __init__(self, config, mac, devtype, firmware, description):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware, description)
        self._rdecimals = self._device_settings["decimals"]

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = round(data[self.entity_description.key], self._rdecimals)
        self._extra_state_attributes["sensor type"] = data["type"]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
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

    def __init__(self, config, mac, devtype, firmware, description):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware, description)
        self._rdecimals = self._device_settings["decimals"]

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = round(data[self.entity_description.key], self._rdecimals)
        self._extra_state_attributes["sensor type"] = data["type"]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
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

    def __init__(self, config, mac, devtype, firmware, description):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware, description)

    def collect(self, data, batt_attr=None):
        """Measurement collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self.entity_description.key]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
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

    def __init__(self, config, mac, devtype, firmware, description):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware, description)
        self._button = "button"
        self._dimmer = self.entity_description.key

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._button] + " " + str(data[self._dimmer]) + " steps"
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
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

    def __init__(self, config, mac, devtype, firmware, description):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware, description)
        self._button_switch = "button switch"
        self._button = self.entity_description.key

    def collect(self, data, batt_attr=None):
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

    def __init__(self, config, mac, devtype, firmware, description):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware, description)
        self._button = "button"
        self._remote = self.entity_description.key

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._button] + " " + data[self._remote]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
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

    def __init__(self, config, mac, devtype, firmware, description):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware, description)

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self.entity_description.key]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes["volume start"] = data["volume start"]
        self._extra_state_attributes["keg size"] = data["keg size"]
        self._extra_state_attributes["port name"] = data["port name"]
        self._extra_state_attributes["port state"] = data["port state"]
        self._extra_state_attributes["port index"] = data["port index"]
        self.pending_update = True
