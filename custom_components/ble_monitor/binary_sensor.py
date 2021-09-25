"""Passive BLE monitor binary sensor platform."""
from datetime import timedelta
import asyncio
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity
)

from homeassistant.const import (
    CONF_DEVICES,
    CONF_NAME,
    CONF_UNIQUE_ID,
    ATTR_BATTERY_LEVEL,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.restore_state import RestoreEntity
import homeassistant.util.dt as dt_util

from .const import (
    CONF_PERIOD,
    CONF_RESTORE_STATE,
    CONF_DEVICE_RESTORE_STATE,
    CONF_DEVICE_RESET_TIMER,
    DEFAULT_DEVICE_RESET_TIMER,
    KETTLES,
    MANUFACTURER_DICT,
    MEASUREMENT_DICT,
    BINARY_SENSOR_TYPES,
    DOMAIN,
    BLEMonitorBinarySensorEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, conf, add_entities, discovery_info=None):
    """Set up from setup_entry."""
    return True


async def async_setup_entry(hass, config_entry, add_entities):
    """Set up the binary sensor platform."""
    _LOGGER.debug("Starting binary sensor entry startup")

    blemonitor = hass.data[DOMAIN]["blemonitor"]
    bleupdater = BLEupdaterBinary(blemonitor, add_entities)
    hass.loop.create_task(bleupdater.async_run(hass))
    _LOGGER.debug("Binary sensor entry setup finished")
    # Return successful setup
    return True


class BLEupdaterBinary:
    """BLE monitor entities updater."""

    def __init__(self, blemonitor, add_entities):
        """Initiate BLE updater."""
        _LOGGER.debug("BLE binary sensors updater initialization")
        self.monitor = blemonitor
        self.dataqueue = blemonitor.dataqueue["binary"].async_q
        self.config = blemonitor.config
        self.period = self.config[CONF_PERIOD]
        self.add_entities = add_entities
        _LOGGER.debug("BLE binary sensors updater initialized")

    async def async_run(self, hass):
        """Entities updater loop."""

        async def async_add_binary_sensor(mac, sensortype, firmware):
            device_sensors = MEASUREMENT_DICT[sensortype][2]
            if mac not in sensors_by_mac:
                sensors = []
                for sensor in device_sensors:
                    description = [item for item in BINARY_SENSOR_TYPES if item.key is sensor][0]
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

        _LOGGER.debug("Binary entities updater loop started!")
        sensors_by_mac = {}
        sensors = []
        batt = {}  # batteries
        mibeacon_cnt = 0
        hpriority = []
        ts_last = dt_util.now()
        ts_now = ts_last
        data = None
        await asyncio.sleep(0)

        # Set up binary sensors of configured devices on startup when sensortype is available in device registry
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
                    if sensortype and firmware:
                        sensors = await async_add_binary_sensor(
                            mac, sensortype, firmware
                        )
                    else:
                        continue
                else:
                    pass
        else:
            sensors = []

        # Set up new binary sensors when first BLE advertisement is received
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
            if len(hpriority) > 0:
                for entity in hpriority:
                    if entity.pending_update is True:
                        hpriority.remove(entity)
                        entity.async_schedule_update_ha_state(True)
            if data:
                _LOGGER.debug("Data binary sensor received: %s", data)
                mibeacon_cnt += 1
                mac = data["mac"]
                batt_attr = None
                sensortype = data["type"]
                firmware = data["firmware"]
                device_sensors = MEASUREMENT_DICT[sensortype][2]
                sensors = await async_add_binary_sensor(mac, sensortype, firmware)

                if data["data"] is False:
                    data = None
                    continue

                # store found readings per device
                if "battery" in MEASUREMENT_DICT[sensortype][0]:
                    if "battery" in data:
                        batt[mac] = int(data["battery"])
                        batt_attr = batt[mac]
                        for entity in sensors:
                            getattr(entity, "_extra_state_attributes")[
                                ATTR_BATTERY_LEVEL
                            ] = batt_attr
                            if entity.pending_update is True:
                                entity.async_schedule_update_ha_state(False)
                    else:
                        try:
                            batt_attr = batt[mac]
                        except KeyError:
                            batt_attr = None
                # schedule an immediate update of binary sensors
                for measurement in device_sensors:
                    if measurement in data:
                        entity = sensors[device_sensors.index(measurement)]
                        entity.collect(data, batt_attr)
                        if entity.pending_update is True:
                            entity.async_schedule_update_ha_state(True)
                        elif (
                            entity.ready_for_update is False and entity.enabled is True
                        ):
                            hpriority.append(entity)
                data = None
            ts_now = dt_util.now()
            if ts_now - ts_last < timedelta(seconds=self.period):
                continue
            ts_last = ts_now
            _LOGGER.debug(
                "%i MiBeacon BLE ADV messages processed for %i binary sensor device(s) total. Priority queue = %i",
                mibeacon_cnt,
                len(sensors_by_mac),
                len(hpriority),
            )
            mibeacon_cnt = 0


class BaseBinarySensor(RestoreEntity, BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(
        self,
        config,
        mac: str,
        devtype: str,
        firmware: str,
        description: BLEMonitorBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        self.entity_description = description
        self._config = config
        self._mac = mac
        self._fmac = ":".join(mac[i : i + 2] for i in range(0, len(self._mac), 2))
        self._state = None

        self._device_settings = self.get_device_settings()
        self._device_name = self._device_settings["name"]
        self._device_type = devtype
        self._device_firmware = firmware
        self._device_manufacturer = MANUFACTURER_DICT[devtype]
        self._extra_state_attributes = {}
        self._extra_state_attributes["sensor type"] = devtype
        self._extra_state_attributes["mac address"] = self._fmac
        self.ready_for_update = False
        self._restore_state = self._device_settings["restore state"]
        self._reset_timer = self._device_settings["reset timer"]
        self._newstate = None

        self._attr_name = f"{description.name} {self._device_name}"
        self._attr_unique_id = f"{description.unique_id}{self._device_name}"
        self._attr_should_poll = False
        self._attr_force_update = description.force_update
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
        self._state = None
        if old_state.state == STATE_ON:
            self._state = True
        elif old_state.state == STATE_OFF:
            self._state = False
        if "rssi" in old_state.attributes:
            self._extra_state_attributes["rssi"] = old_state.attributes["rssi"]
        if "firmware" in old_state.attributes:
            self._extra_state_attributes["firmware"] = old_state.attributes["firmware"]
        if "last packet id" in old_state.attributes:
            self._extra_state_attributes["last packet id"] = old_state.attributes[
                "last packet id"
            ]
        if ATTR_BATTERY_LEVEL in old_state.attributes:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = old_state.attributes[
                ATTR_BATTERY_LEVEL
            ]
        if "status" in old_state.attributes:
            self._extra_state_attributes["status"] = old_state.attributes["status"]
        if "motion timer" in old_state.attributes:
            self._extra_state_attributes["motion timer"] = old_state.attributes[
                "motion timer"
            ]
        if "action" in old_state.attributes:
            self._extra_state_attributes["action"] = old_state.attributes["action"]
        if "method" in old_state.attributes:
            self._extra_state_attributes["method"] = old_state.attributes["method"]
        if "error" in old_state.attributes:
            self._extra_state_attributes["error"] = old_state.attributes["error"]
        if "key id" in old_state.attributes:
            self._extra_state_attributes["key id"] = old_state.attributes["key id"]
        if "timestamp" in old_state.attributes:
            self._extra_state_attributes["timestamp"] = old_state.attributes["timestamp"]
        if "result" in old_state.attributes:
            self._extra_state_attributes["result"] = old_state.attributes["result"]
        if "score" in old_state.attributes:
            self._extra_state_attributes["score"] = old_state.attributes["score"]
        if "counter" in old_state.attributes:
            self._extra_state_attributes["counter"] = old_state.attributes["counter"]

        self.ready_for_update = True

    @property
    def pending_update(self):
        """Check if entity is enabled."""
        return self.enabled and self.ready_for_update

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return bool(self._state) if self._state is not None else None

    def get_device_settings(self):
        """Set device settings."""
        device_settings = {}

        # initial setup of device settings equal to integration settings
        dev_name = self._mac
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
                    if CONF_DEVICE_RESTORE_STATE in device:
                        if isinstance(device[CONF_DEVICE_RESTORE_STATE], bool):
                            dev_restore_state = device[CONF_DEVICE_RESTORE_STATE]
                        else:
                            dev_restore_state = self._config[CONF_RESTORE_STATE]
                    if CONF_DEVICE_RESET_TIMER in device:
                        dev_reset_timer = device[CONF_DEVICE_RESET_TIMER]
        device_settings = {
            "name": dev_name,
            "restore state": dev_restore_state,
            "reset timer": dev_reset_timer,
        }
        _LOGGER.debug(
            "Binary sensor device with mac address %s has the following settings. "
            "Name: %s. "
            "Restore state: %s. "
            "Reset Timer: %s",
            self._fmac,
            device_settings["name"],
            device_settings["restore state"],
            device_settings["reset timer"],
        )
        return device_settings

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            return
        self._newstate = data[self.entity_description.key]
        self._extra_state_attributes["last packet id"] = data["packet"]
        self._extra_state_attributes["rssi"] = data["rssi"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        if "motion timer" in data:
            if data["motion timer"] == 1:
                self._extra_state_attributes["last motion"] = dt_util.now()
        # dirty hack for kettle status
        if self._device_type in KETTLES:
            if self._newstate == 0:
                self._extra_state_attributes["status"] = "kettle is idle"
            elif self._newstate == 1:
                self._extra_state_attributes["status"] = "kettle is heating"
            elif self._newstate == 2:
                self._extra_state_attributes["status"] = "warming function active with boiling"
            elif self._newstate == 3:
                self._extra_state_attributes["status"] = "warming function active without boiling"
            else:
                self._extra_state_attributes["status"] = self._newstate
        if self.entity_description.key == "opening":
            self._extra_state_attributes["status"] = data["status"]
        if self.entity_description.key == "lock":
            self._extra_state_attributes["action"] = data["action"]
            self._extra_state_attributes["method"] = data["method"]
            self._extra_state_attributes["error"] = data["error"]
            self._extra_state_attributes["key id"] = data["key id"]
            self._extra_state_attributes["timestamp"] = data["timestamp"]
        if self.entity_description.key == "fingerprint":
            self._extra_state_attributes["result"] = data["result"]
            self._extra_state_attributes["key id"] = data["key id"]
        if self.entity_description.key == "toothbrush":
            if "counter" in data:
                self._extra_state_attributes["counter"] = data["counter"]
            else:
                self._extra_state_attributes["score"] = data["score"]

    async def async_update(self):
        """Update sensor state and attribute."""
        self._state = self._newstate


class MotionBinarySensor(BaseBinarySensor):
    """Representation of a Motion Binary Sensor."""

    def __init__(self, config, mac, devtype, firmware, description):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype, firmware, description)
        self._start_timer = None

    def reset_state(self, event=None):
        """Reset state of the sensor."""
        # check if the latest update of the timer is longer than the set timer value
        if dt_util.now() - self._start_timer >= timedelta(seconds=self._reset_timer):
            self._state = False
            self.schedule_update_ha_state(False)

    async def async_update(self):
        """Update sensor state and attribute."""
        # check if the reset timer is enabled
        if self._reset_timer > 0:
            try:
                # if there is a last motion attribute, check the timer
                now = dt_util.now()
                self._start_timer = self._extra_state_attributes["last motion"]

                if now - self._start_timer >= timedelta(seconds=self._reset_timer):
                    self._state = False
                else:
                    self._state = True
                    async_call_later(self.hass, self._reset_timer, self.reset_state)
            except KeyError:
                self._state = self._newstate
        else:
            self._state = self._newstate
