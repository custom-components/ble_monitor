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
    CONF_MAC,
    CONF_UNIQUE_ID,
    ATTR_BATTERY_LEVEL,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt

from .helper import (
    identifier_normalize,
    identifier_clean,
    detect_conf_type,
    dict_get_or,
    dict_get_or_normalize,
)

from .const import (
    AUTO_MANUFACTURER_DICT,
    AUTO_BINARY_SENSOR_LIST,
    CONF_PERIOD,
    CONF_RESTORE_STATE,
    CONF_DEVICE_RESTORE_STATE,
    CONF_DEVICE_RESET_TIMER,
    CONF_UUID,
    DEFAULT_DEVICE_RESET_TIMER,
    KETTLES,
    MANUFACTURER_DICT,
    MEASUREMENT_DICT,
    BINARY_SENSOR_TYPES,
    DOMAIN,
    BLEMonitorBinarySensorEntityDescription,
)

_LOGGER = logging.getLogger(__name__)

RESTORE_ATTRIBUTES = [
    "rssi",
    "firmware",
    "last_packet_id",
    ATTR_BATTERY_LEVEL,
    "status",
    "last_motion",
    "action",
    "method",
    "error",
    "key_id",
    "timestamp",
    "result",
    "counter",
    "score",
    "toothbrush_state",
    "pressure",
    "mode",
    "sector_timer",
    "number_of_sectors",
    "weight",
]


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

        async def async_add_binary_sensor(key, sensortype, firmware, manufacturer=None, data={}):
            if sensortype in AUTO_MANUFACTURER_DICT:
                sensors = {}
                for measurement in AUTO_BINARY_SENSOR_LIST:
                    if measurement in data:
                        if key not in sensors_by_key:
                            sensors_by_key[key] = {}
                        if measurement not in sensors_by_key[key]:
                            description = [item for item in BINARY_SENSOR_TYPES if item.key is measurement][0]
                            sensors[measurement] = globals()[description.sensor_class](
                                self.config, key, sensortype, firmware, description, manufacturer
                            )
                            self.add_entities([sensors[measurement]])
                            sensors_by_key[key].update(sensors)
                        else:
                            sensors = sensors_by_key[key]
            else:
                device_sensors = MEASUREMENT_DICT[sensortype][2]
                if key not in sensors_by_key:
                    sensors = {}
                    sensors_by_key[key] = {}
                    for measurement in device_sensors:
                        description = [item for item in BINARY_SENSOR_TYPES if item.key is measurement][0]
                        sensors[measurement] = globals()[description.sensor_class](
                            self.config, key, sensortype, firmware, description, manufacturer
                        )
                        self.add_entities([sensors[measurement]])
                    sensors_by_key[key] = sensors
                else:
                    sensors = sensors_by_key[key]
            return sensors

        _LOGGER.debug("Binary entities updater loop started!")
        sensors_by_key = {}
        sensors = {}
        batt = {}  # batteries
        mibeacon_cnt = 0
        hpriority = []
        ts_last = dt.now()
        ts_now = ts_last
        data = {}
        await asyncio.sleep(0)

        # Set up binary sensors of configured devices on startup when sensortype is available in device registry
        if self.config[CONF_DEVICES]:
            dev_registry = await hass.helpers.device_registry.async_get_registry()
            for device in self.config[CONF_DEVICES]:
                key = dict_get_or(device)

                # get sensortype and firmware from device registry to setup sensor
                dev = dev_registry.async_get_device({(DOMAIN, key.upper())}, set())
                if dev:
                    key = identifier_clean(key)
                    sensortype = dev.model
                    firmware = dev.sw_version
                    if sensortype and firmware:
                        sensors = await async_add_binary_sensor(
                            key, sensortype, firmware, dev.manufacturer, data
                        )
                    else:
                        continue
                else:
                    pass
        else:
            sensors = {}

        # Set up new binary sensors when first BLE advertisement is received
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
            if len(hpriority) > 0:
                for entity in hpriority:
                    if entity.pending_update is True:
                        hpriority.remove(entity)
                        entity.async_schedule_update_ha_state(True)
            if data:
                _LOGGER.debug("Data binary sensor received: %s", data)
                mibeacon_cnt += 1
                key = dict_get_or(data)
                batt_attr = None
                sensortype = data["type"]
                firmware = data["firmware"]
                manufacturer = data["manufacturer"] if "manufacturer" in data else None
                sensors = await async_add_binary_sensor(key, sensortype, firmware, manufacturer, data)
                device_sensors = sensors.keys()

                if data["data"] is False:
                    data = None
                    continue

                # battery attribute
                if sensortype in AUTO_MANUFACTURER_DICT or (
                    sensortype in MANUFACTURER_DICT and (
                        "battery" in MEASUREMENT_DICT[sensortype][0]
                    )
                ):
                    if "battery" in data:
                        batt[key] = int(data["battery"])
                        batt_attr = batt[key]
                        for entity in sensors.values():
                            getattr(entity, "_extra_state_attributes")[
                                ATTR_BATTERY_LEVEL
                            ] = batt_attr
                            if entity.pending_update is True:
                                entity.async_schedule_update_ha_state(False)
                    else:
                        try:
                            batt_attr = batt[key]
                        except KeyError:
                            batt_attr = None

                # schedule an immediate update of binary sensors
                for measurement in device_sensors:
                    if measurement in data:
                        entity = sensors[measurement]
                        entity.collect(data, batt_attr)
                        if entity.pending_update is True:
                            entity.async_schedule_update_ha_state(True)
                        elif (
                            entity.ready_for_update is False and entity.enabled is True
                        ):
                            hpriority.append(entity)
                data = None
            ts_now = dt.now()
            if ts_now - ts_last < timedelta(seconds=self.period):
                continue
            ts_last = ts_now
            _LOGGER.debug(
                "%i MiBeacon BLE ADV messages processed for %i binary sensor device(s) total. Priority queue = %i",
                mibeacon_cnt,
                len(sensors_by_key),
                len(hpriority),
            )
            mibeacon_cnt = 0


class BaseBinarySensor(RestoreEntity, BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(
        self,
        config,
        key: str,
        devtype: str,
        firmware: str,
        description: BLEMonitorBinarySensorEntityDescription,
        manufacturer=None
    ) -> None:
        """Initialize the binary sensor."""
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
            else MANUFACTURER_DICT.get(
                devtype,
                AUTO_MANUFACTURER_DICT.get(devtype, None)
            )

        self._extra_state_attributes = {
            'sensor_type': devtype,
            'uuid' if self.is_beacon else 'mac_address': self._fkey
        }

        self.ready_for_update = False
        self._restore_state = self._device_settings["restore_state"]
        self._reset_timer = self._device_settings["reset_timer"]
        self._newstate = None

        self._attr_name = f"{description.name} {self._device_name}"
        self._attr_unique_id = f"{description.unique_id}{self._device_name}"
        self._attr_should_poll = False
        self._attr_force_update = description.force_update
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
        self._state = None
        if old_state.state == STATE_ON:
            self._state = True
        elif old_state.state == STATE_OFF:
            self._state = False

        restore_attr = RESTORE_ATTRIBUTES
        restore_attr.append('mac_address' if self.is_beacon else 'uuid')

        for attr in restore_attr:
            if attr in old_state.attributes:
                if attr in ['uuid', 'mac_address']:
                    self._extra_state_attributes[attr] = identifier_normalize(old_state.attributes[attr])
                    continue

                self._extra_state_attributes[attr] = old_state.attributes[attr]
        self.ready_for_update = True

    @property
    def is_beacon(self):
        """Check if entity is beacon."""
        return self._type == CONF_UUID

    @property
    def pending_update(self):
        """Check if entity is enabled."""
        return self.enabled and self.ready_for_update

    @property
    def entity_registry_enabled_default(self):
        """Return if the entity should be enabled when first added to the entity registry."""
        if self._device_type == "ATC":
            return False
        else:
            return True

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return bool(self._state) if self._state is not None else None

    def get_device_settings(self):
        """Set device settings."""
        device_settings = {}

        # initial setup of device settings equal to integration settings
        dev_name = self._key
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
                    if CONF_DEVICE_RESTORE_STATE in device:
                        if isinstance(device[CONF_DEVICE_RESTORE_STATE], bool):
                            dev_restore_state = device[CONF_DEVICE_RESTORE_STATE]
                        else:
                            dev_restore_state = self._config[CONF_RESTORE_STATE]
                    if CONF_DEVICE_RESET_TIMER in device:
                        dev_reset_timer = device[CONF_DEVICE_RESET_TIMER]
        device_settings = {
            "name": dev_name,
            "restore_state": dev_restore_state,
            "reset_timer": dev_reset_timer,
        }
        _LOGGER.debug(
            "Binary sensor device with %s %s has the following settings. "
            "Name: %s. "
            "Restore State: %s. "
            "Reset Timer: %s",
            'uuid' if self.is_beacon else 'mac address',
            self._fkey,
            device_settings["name"],
            device_settings["restore_state"],
            device_settings["reset_timer"],
        )
        return device_settings

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.enabled is False:
            return
        self._newstate = data[self.entity_description.key]
        self._extra_state_attributes["last_packet_id"] = data["packet"]
        self._extra_state_attributes["rssi"] = data["rssi"]
        self._extra_state_attributes["firmware"] = data["firmware"]
        self._extra_state_attributes['mac_address' if self.is_beacon else 'uuid'] = dict_get_or_normalize(
            data, CONF_MAC, CONF_UUID
        )

        if batt_attr is not None:
            self._extra_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr
        if "motion timer" in data:
            if data["motion timer"] == 1:
                self._extra_state_attributes["last_motion"] = dt.now()
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
            if "status" in data:
                self._extra_state_attributes["status"] = data["status"]
        if self.entity_description.key == "lock":
            self._extra_state_attributes["action"] = data["action"]
            self._extra_state_attributes["method"] = data["method"]
            self._extra_state_attributes["error"] = data["error"]
            self._extra_state_attributes["key_id"] = data["key id"]
            self._extra_state_attributes["timestamp"] = data["timestamp"]
        if self.entity_description.key == "fingerprint":
            self._extra_state_attributes["result"] = data["result"]
            self._extra_state_attributes["key_id"] = data["key id"]
        if self.entity_description.key == "toothbrush":
            if "counter" in data:
                self._extra_state_attributes["counter"] = data["counter"]
            if "score" in data:
                self._extra_state_attributes["score"] = data["score"]
            if "toothbrush state" in data:
                self._extra_state_attributes["toothbrush_state"] = data["toothbrush state"]
            if "pressure" in data:
                self._extra_state_attributes["pressure"] = data["pressure"]
            if "mode" in data:
                self._extra_state_attributes["mode"] = data["mode"]
            if "sector timer" in data:
                self._extra_state_attributes["sector_timer"] = data["sector timer"]
            if "number of sectors" in data:
                self._extra_state_attributes["number_of_sectors"] = data["number of sectors"]
        if self.entity_description.key == "weight removed":
            if "stabilized" in data:
                if data["stabilized"] and data["weight removed"]:
                    self._extra_state_attributes["weight"] = data["non-stabilized weight"]

    async def async_update(self):
        """Update sensor state and attribute."""
        self._state = self._newstate


class MotionBinarySensor(BaseBinarySensor):
    """Representation of a Motion Binary Sensor."""

    def __init__(self, config, key, devtype, firmware, description, manufacturer=None):
        """Initialize the sensor."""
        super().__init__(config, key, devtype, firmware, description, manufacturer)
        self._start_timer = None

    def reset_state(self, event=None):
        """Reset state of the sensor."""
        # check if the latest update of the timer is longer than the set timer value
        if dt.now() - self._start_timer >= timedelta(seconds=self._reset_timer):
            self._state = False
            self.schedule_update_ha_state(False)

    async def async_update(self):
        """Update sensor state and attribute."""
        # check if the reset timer is enabled
        if self._reset_timer > 0:
            try:
                # if there is a last_motion attribute, check the timer
                now = dt.now()
                self._start_timer = self._extra_state_attributes["last_motion"]
                if type(self._start_timer) is str:
                    self._start_timer = dt.parse_datetime(self._start_timer)

                if now - self._start_timer >= timedelta(seconds=self._reset_timer):
                    self._state = False
                else:
                    self._state = True
                    async_call_later(self.hass, self._reset_timer, self.reset_state)
            except (KeyError, ValueError):
                self._state = self._newstate
        else:
            self._state = self._newstate
