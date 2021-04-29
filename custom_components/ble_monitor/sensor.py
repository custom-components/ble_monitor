"""Passive BLE monitor sensor platform."""
from datetime import timedelta
import asyncio
import logging
import statistics as sts

from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_VOLTAGE,
    CONDUCTIVITY,
    PRESSURE_HPA,
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

from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.restore_state import RestoreEntity
import homeassistant.util.dt as dt_util

from .const import (
    CONF_DECIMALS,
    CONF_PERIOD,
    CONF_LOG_SPIKES,
    CONF_USE_MEDIAN,
    CONF_BATT_ENTITIES,
    CONF_RESTORE_STATE,
    CONF_DEVICE_DECIMALS,
    CONF_DEVICE_USE_MEDIAN,
    CONF_DEVICE_RESTORE_STATE,
    CONF_DEVICE_RESET_TIMER,
    CONF_TMIN,
    CONF_TMAX,
    CONF_HMIN,
    CONF_HMAX,
    DEFAULT_DEVICE_RESET_TIMER,
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
        self.log_spikes = self.config[CONF_LOG_SPIKES]
        self.batt_entities = self.config[CONF_BATT_ENTITIES]
        self.add_entities = add_entities
        _LOGGER.debug("BLE sensors updater initialized")

    async def async_run(self, hass):
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

        async def async_add_sensor(mac, sensortype, firmware):
            t_i, h_i, m_i, p_i, c_i, i_i, f_i, cn_i, bu_i, w_i, nw_i, im_i, vd_i, to_i, v_i, b_i = MMTS_DICT[sensortype][0]
            if mac not in sensors_by_mac:
                sensors = []
                if t_i != 9:
                    sensors.insert(t_i, TemperatureSensor(self.config, mac, sensortype, firmware))
                if h_i != 9:
                    sensors.insert(h_i, HumiditySensor(self.config, mac, sensortype, firmware))
                if m_i != 9:
                    sensors.insert(m_i, MoistureSensor(self.config, mac, sensortype, firmware))
                if p_i != 9:
                    sensors.insert(p_i, PressureSensor(self.config, mac, sensortype, firmware))
                if c_i != 9:
                    sensors.insert(c_i, ConductivitySensor(self.config, mac, sensortype, firmware))
                if i_i != 9:
                    sensors.insert(i_i, IlluminanceSensor(self.config, mac, sensortype, firmware))
                if f_i != 9:
                    sensors.insert(f_i, FormaldehydeSensor(self.config, mac, sensortype, firmware))
                if cn_i != 9:
                    sensors.insert(cn_i, ConsumableSensor(self.config, mac, sensortype, firmware))
                if bu_i != 9:
                    sensors.insert(bu_i, ButtonSensor(self.config, mac, sensortype, firmware))
                if w_i != 9:
                    sensors.insert(w_i, WeightSensor(self.config, mac, sensortype, firmware))
                if nw_i != 9:
                    sensors.insert(nw_i, NonStabilizedWeightSensor(self.config, mac, sensortype, firmware))
                if im_i != 9:
                    sensors.insert(im_i, ImpedanceSensor(self.config, mac, sensortype, firmware))
                if vd_i != 9:
                    port = 1
                    sensors.insert(vd_i, VolumeDispensedSensor(self.config, mac, sensortype, port, firmware))
                    if sensortype == "Kegtron KT-200":
                        port = 2
                        sensors.insert(vd_i + 1, VolumeDispensedSensor(self.config, mac, sensortype, port, firmware))
                if to_i != 9:
                    sensors.insert(to_i, ToothbrushModeSensor(self.config, mac, sensortype, firmware))
                if self.batt_entities and (v_i != 9):
                    sensors.insert(v_i, VoltageSensor(self.config, mac, sensortype, firmware))
                if self.batt_entities and (b_i != 9):
                    sensors.insert(b_i, BatterySensor(self.config, mac, sensortype, firmware))
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
                    firmware = dev.sw_version
                    sensors = await async_add_sensor(mac, sensortype, firmware)
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
                firmware = data["firmware"]
                t_i, h_i, m_i, p_i, c_i, i_i, f_i, cn_i, bu_i, w_i, nw_i, im_i, vd_i, to_i, v_i, b_i = MMTS_DICT[sensortype][0]
                sensors = await async_add_sensor(mac, sensortype, firmware)

                if data["data"] is False:
                    data = None
                    continue

                # store found readings per device
                # battery sensors and battery attribute
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
                if "temperature" in data and (t_i != 9):
                    # schedule an immediate update of kettle temperature
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
                            temperature_limit(
                                self.config, mac, CONF_TMAX
                            ) >= data["temperature"] >= temperature_limit(self.config, mac, CONF_TMIN)
                        ):
                            sensors[t_i].collect(data, batt_attr)
                        elif self.log_spikes:
                            _LOGGER.error(
                                "Temperature spike: %s (%s)",
                                data["temperature"],
                                mac,
                            )
                if "humidity" in data and (h_i != 9):
                    if CONF_HMAX >= data["humidity"] >= CONF_HMIN:
                        sensors[h_i].collect(data, batt_attr)
                    elif self.log_spikes:
                        _LOGGER.error(
                            "Humidity spike: %s (%s)",
                            data["humidity"],
                            mac,
                        )
                if "conductivity" in data and (c_i != 9):
                    sensors[c_i].collect(data, batt_attr)
                if "pressure" in data and (p_i != 9):
                    sensors[p_i].collect(data, batt_attr)
                if "moisture" in data and (m_i != 9):
                    sensors[m_i].collect(data, batt_attr)
                if "illuminance" in data and (i_i != 9):
                    sensors[i_i].collect(data, batt_attr)
                if "formaldehyde" in data and (f_i != 9):
                    sensors[f_i].collect(data, batt_attr)
                if "consumable" in data and (cn_i != 9):
                    sensors[cn_i].collect(data, batt_attr)
                if "button" in data and (bu_i != 9):
                    button = sensors[bu_i]
                    # schedule an immediate update of button sensors
                    button.collect(data, batt_attr)
                    if button.ready_for_update is True:
                        button.rssi_values = rssi[mac].copy()
                        button.async_schedule_update_ha_state(True)
                        button.pending_update = False
                if "weight" in data and (w_i != 9):
                    weight = sensors[w_i]
                    # schedule an immediate update of weight sensors
                    weight.collect(data, batt_attr)
                    if weight.ready_for_update is True:
                        weight.rssi_values = rssi[mac].copy()
                        weight.async_schedule_update_ha_state(True)
                        weight.pending_update = False
                if "non-stabilized weight" in data and (nw_i != 9):
                    non_stabilized_weight = sensors[nw_i]
                    # schedule an immediate update of non-stabilized weight sensors
                    non_stabilized_weight.collect(data, batt_attr)
                    if non_stabilized_weight.ready_for_update is True:
                        non_stabilized_weight.rssi_values = rssi[mac].copy()
                        non_stabilized_weight.async_schedule_update_ha_state(True)
                        non_stabilized_weight.pending_update = False
                if "impedance" in data and (im_i != 9):
                    impedance = sensors[im_i]
                    # schedule an immediate update of impedance sensors
                    impedance.collect(data, batt_attr)
                    if impedance.ready_for_update is True:
                        impedance.rssi_values = rssi[mac].copy()
                        impedance.async_schedule_update_ha_state(True)
                        impedance.pending_update = False
                if "volume dispensed" in data and (vd_i != 9):
                    port = data["port index"]
                    vd_i = vd_i + port - 1
                    volume_dispensed = sensors[vd_i]
                    # schedule an immediate update of kegtron volume dispensed sensors
                    volume_dispensed.collect(data, batt_attr)
                    if volume_dispensed.ready_for_update is True:
                        volume_dispensed.rssi_values = rssi[mac].copy()
                        volume_dispensed.async_schedule_update_ha_state(True)
                        volume_dispensed.pending_update = False
                if "toothbrush mode" in data and (to_i != 9):
                    toothbrushmode = sensors[to_i]
                    # schedule an immediate update of toothbrush mode sensors
                    toothbrushmode.collect(data, batt_attr)
                    if toothbrushmode.ready_for_update is True:
                        toothbrushmode.rssi_values = rssi[mac].copy()
                        toothbrushmode.async_schedule_update_ha_state(True)
                        toothbrushmode.pending_update = False
                if self.batt_entities:
                    if "voltage" in data and (v_i != 9):
                        sensors[v_i].collect(data, batt_attr)
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


class MeasuringSensor(RestoreEntity):
    """Base class for measuring sensor entity."""

    def __init__(self, config, mac, devtype, firmware):
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
        self._rdecimals = self._device_settings["decimals"]
        self._jagged = False
        self._fmdh_dec = 0
        self._use_median = self._device_settings["use median"]
        self._restore_state = self._device_settings["restore state"]
        self._reset_timer = self._device_settings["reset timer"]
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
            "sw_version": self._device_firmware,
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
        # LYWSD03MMC / MHO-C401 "jagged" humidity workaround
        if devtype in ('LYWSD03MMC', 'MHO-C401'):
            if self._device_firmware == "Xiaomi (MiBeacon)":
                self._jagged = True


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


class ConsumableSensor(MeasuringSensor):
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

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    async def async_update(self):
        """Update."""
        self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False


class ButtonSensor(MeasuringSensor):
    """Representation of a Button sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "button"
        self._name = "ble button {}".format(self._device_name)
        self._unique_id = "bu_" + self._device_name
        self._unit_of_measurement = None
        self._device_class = None

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:gesture-tap-button"

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
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
        self._device_state_attributes["last button press"] = self._state
        async_call_later(self.hass, 1, self.reset_state)
        self.rssi_values.clear()
        self.pending_update = False


class WeightSensor(MeasuringSensor):
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

    async def async_update(self):
        """Update."""
        self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False


class NonStabilizedWeightSensor(MeasuringSensor):
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

    async def async_update(self):
        """Update."""
        self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False


class ImpedanceSensor(MeasuringSensor):
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

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    async def async_update(self):
        """Update."""
        self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False


class VolumeDispensedSensor(MeasuringSensor):
    """Representation of a Kegtron Volume dispensed sensor."""

    def __init__(self, config, mac, devtype, port, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "volume dispensed"
        self._port = port
        self._name = "ble volume dispensed port {} {}".format(self._port, self._device_name)
        self._unique_id = "vd_" + str(self._port) + "_" + self._device_name
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

    async def async_update(self):
        """Update."""
        self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False


class ToothbrushModeSensor(MeasuringSensor):
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

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            self.pending_update = False
            return
        self._state = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        self.pending_update = True

    async def async_update(self):
        """Update."""
        self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False


class VoltageSensor(MeasuringSensor):
    """Representation of a Voltage sensor."""

    def __init__(self, config, mac, devtype, firmware):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware)
        self._measurement = "voltage"
        self._name = "ble voltage {}".format(self._device_name)
        self._unique_id = "v_" + self._device_name
        self._unit_of_measurement = VOLT
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
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["firmware"] = data["firmware"]
        self.pending_update = True

    async def async_update(self):
        """Update sensor state and attributes."""
        self._device_state_attributes["rssi"] = round(sts.mean(self.rssi_values))
        self.rssi_values.clear()
        self.pending_update = False
