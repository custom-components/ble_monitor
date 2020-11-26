"""Passive BLE monitor sensor platform."""
from datetime import timedelta
import logging
import queue
import statistics as sts
from threading import Thread

from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_TEMPERATURE,
    CONDUCTIVITY,
    PERCENTAGE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    ATTR_BATTERY_LEVEL,
)
from homeassistant.helpers.restore_state import RestoreEntity
import homeassistant.util.dt as dt_util

from . import (
    CONF_DEVICES,
    CONF_ROUNDING,
    CONF_DECIMALS,
    CONF_PERIOD,
    CONF_LOG_SPIKES,
    CONF_USE_MEDIAN,
    CONF_HCI_INTERFACE,
    CONF_BATT_ENTITIES,
    CONF_RESTORE_STATE,
)
from .const import (
    CONF_TMIN,
    CONF_TMAX,
    CONF_HMIN,
    CONF_HMAX,
    DEFAULT_HCI_INTERFACE,
    MANUFACTURER_DICT,
    MMTS_DICT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, conf, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    _LOGGER.debug("Sensor platform setup")
    blemonitor = hass.data[DOMAIN]
    bleupdater = BLEupdater(blemonitor, add_entities)
    bleupdater.start()
    _LOGGER.debug("Sensor platform setup finished")
    # Return successful setup
    return True


async def async_setup_entry(hass, config_entry, add_entities):
    """Set up the sensor platform."""
    _LOGGER.debug("Platform startup")

    config = {}
    for key, value in config_entry.options.items():
        config[key] = value

    if not config[CONF_HCI_INTERFACE]:
        config[CONF_HCI_INTERFACE] = [DEFAULT_HCI_INTERFACE,]
    else:
        hci_list = config_entry.options.get(CONF_HCI_INTERFACE)
        for hci in range(0, len(hci_list)): 
            hci_list[hci] = int(hci_list[hci])
        config[CONF_HCI_INTERFACE] = hci_list
    _LOGGER.debug("HCI interface is %s", config[CONF_HCI_INTERFACE])
    if not CONF_DEVICES in config:
        config[CONF_DEVICES] = []
    blemonitor = hass.data[DOMAIN]
    bleupdater = BLEupdater(blemonitor, add_entities)
    bleupdater.start()
    _LOGGER.debug("Platform setup finished")
    # Return successful setup
    return True


class BLEupdater(Thread):
    """BLE monitor entities updater."""

    def __init__(self, blemonitor, add_entities):
        """Initiate BLE updater."""
        Thread.__init__(self, daemon=True)
        _LOGGER.debug("BLE sensors updater initialization")
        self.monitor = blemonitor
        self.dataqueue = blemonitor.dataqueue["measuring"]
        self.config = blemonitor.config
        self.period = self.config[CONF_PERIOD]
        self.log_spikes = self.config[CONF_LOG_SPIKES]
        self.batt_entities = self.config[CONF_BATT_ENTITIES]
        self.add_entities = add_entities
        _LOGGER.debug("BLE sensors updater initialized")

    def run(self):
        """Entities updater loop."""

        def temperature_limit(config, mac, temp):
            """Set limits for temperature measurement in °C or °F."""
            fmac = ':'.join(mac[i:i + 2] for i in range(0, len(mac), 2))

            if config[CONF_DEVICES]:
                for device in config[CONF_DEVICES]:
                    if fmac in device["mac"].upper():
                        if "temperature_unit" in device:
                            if device["temperature_unit"] == TEMP_FAHRENHEIT:
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
        ts_last = dt_util.now()
        ts_now = ts_last
        data = None
        while True:
            try:
                advevent = self.dataqueue.get(block=True, timeout=1)
                if advevent is None:
                    _LOGGER.debug("Entities updater loop stopped")
                    return True
                data = advevent
            except queue.Empty:
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
                t_i, h_i, m_i, c_i, i_i, f_i, cn_i, b_i = MMTS_DICT[sensortype][0]
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
                    if self.batt_entities and (b_i != 9):
                        sensors.insert(b_i, BatterySensor(self.config, mac, sensortype))
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
                    sensors[i_i].collect(data, batt_attr)
                if "formaldehyde" in data:
                    sensors[f_i].collect(data, batt_attr)
                if "consumable" in data:
                    sensors[cn_i].collect(data, batt_attr)
                data = None
            ts_now = dt_util.now()
            if ts_now - ts_last < timedelta(seconds=self.period):
                continue
            ts_last = ts_now
            # restarting scanner
            self.monitor.restart()
            # for every updated device
            upd_evt = False
            for mac, elist in sensors_by_mac.items():
                for entity in elist:
                    if entity.pending_update is True:
                        if entity.ready_for_update is True:
                            entity.rssi_values = rssi[mac].copy()
                            entity.schedule_update_ha_state(True)
                            upd_evt = True
                if upd_evt:
                    rssi[mac].clear()
                upd_evt = False
            rssi.clear()

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
        self._name = ""
        self._state = None
        self._unit_of_measurement = ""
        self._device_class = None
        self._device_type = devtype
        self._device_manufacturer = MANUFACTURER_DICT[devtype]
        self._device_state_attributes = {}
        self._device_state_attributes["sensor type"] = devtype
        self._device_state_attributes["mac address"] = (
            ':'.join(mac[i:i + 2] for i in range(0, len(mac), 2))
        )
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
        self._state = old_state.state
        if "median" in old_state.attributes:
            self._device_state_attributes["median"] = old_state.attributes["median"]
        if "mean" in old_state.attributes:
            self._device_state_attributes["mean"] = old_state.attributes["mean"]
        if "last median of" in old_state.attributes:
            self._device_state_attributes["last median of"] = old_state.attributes["last median of"]
        if "last mean of" in old_state.attributes:
            self._device_state_attributes["last mean of"] = old_state.attributes["last mean of"]
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
        return {
            "identifiers": {
                # Unique identifiers within a specific domain
                (DOMAIN, self.get_sensorname())
            },
            "name": self.get_sensorname(),
            "model": self._device_type,
            "manufacturer": self._device_manufacturer,
        }

    @property
    def force_update(self):
        """Force update."""
        return True

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self._jagged is True:
            self._measurements.append(int(data[self._measurement]))
        else:
            self._measurements.append(data[self._measurement])
        self._device_state_attributes["last packet id"] = data["packet"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    def update(self):
        """Updates sensor state and attributes."""
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

    def get_sensorname(self):
        """Set sensor name."""
        fmac = ":".join(self._mac[i:i + 2] for i in range(0, len(self._mac), 2))

        if self._config[CONF_DEVICES]:
            for device in self._config[CONF_DEVICES]:
                if fmac in device["mac"].upper():
                    if "name" in device:
                        custom_name = device["name"]
                        _LOGGER.debug(
                            "Name of %s sensor with mac adress %s is set to: %s",
                            self._measurement,
                            fmac,
                            custom_name,
                        )
                        return custom_name
                    break
        return self._mac


class TemperatureSensor(MeasuringSensor):
    """Representation of a sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "temperature"
        self._sensor_name = self.get_sensorname()
        self._name = "ble temperature {}".format(self._sensor_name)
        self._unique_id = "t_" + self._sensor_name
        self._unit_of_measurement = self.get_temperature_unit()
        self._device_class = DEVICE_CLASS_TEMPERATURE

    def get_temperature_unit(self):
        """Set temperature unit to °C or °F."""
        fmac = ":".join(self._mac[i:i + 2] for i in range(0, len(self._mac), 2))

        if self._config[CONF_DEVICES]:
            for device in self._config[CONF_DEVICES]:
                if fmac in device["mac"].upper():
                    if "temperature_unit" in device:
                        _LOGGER.debug(
                            "Temperature sensor with mac address %s is set to receive data in %s",
                            fmac,
                            device["temperature_unit"],
                        )
                        return device["temperature_unit"]
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
        self._sensor_name = self.get_sensorname()
        self._name = "ble humidity {}".format(self._sensor_name)
        self._unique_id = "h_" + self._sensor_name
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
        self._sensor_name = self.get_sensorname()
        self._name = "ble moisture {}".format(self._sensor_name)
        self._unique_id = "m_" + self._sensor_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = DEVICE_CLASS_HUMIDITY


class ConductivitySensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "conductivity"
        self._sensor_name = self.get_sensorname()
        self._name = "ble conductivity {}".format(self._sensor_name)
        self._unique_id = "c_" + self._sensor_name
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
        self._sensor_name = self.get_sensorname()
        self._name = "ble illuminance {}".format(self._sensor_name)
        self._unique_id = "l_" + self._sensor_name
        self._unit_of_measurement = "lx"
        self._device_class = DEVICE_CLASS_ILLUMINANCE


class FormaldehydeSensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "formaldehyde"
        self._sensor_name = self.get_sensorname()
        self._name = "ble formaldehyde {}".format(self._sensor_name)
        self._unique_id = "f_" + self._sensor_name
        self._unit_of_measurement = "mg/m³"
        self._device_class = None
        self._fmdh_dec = 3

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:chemical-weapon"


class BatterySensor(MeasuringSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "battery"
        self._sensor_name = self.get_sensorname()
        self._name = "ble battery {}".format(self._sensor_name)
        self._unique_id = "batt_" + self._sensor_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = DEVICE_CLASS_BATTERY

    def collect(self, data, batt_attr=None):
        """Battery measurements collector."""
        self._state = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        self.pending_update = True

    def update(self):
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
        self._sensor_name = self.get_sensorname()
        self._name = "ble consumable {}".format(self._sensor_name)
        self._unique_id = "cn_" + self._sensor_name
        self._unit_of_measurement = PERCENTAGE
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:mdi-recycle-variant"

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        self._state = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    def update(self):
        """Update."""
        self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False
