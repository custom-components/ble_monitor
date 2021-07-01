"""Passive BLE monitor binary sensor platform."""
from datetime import timedelta
import asyncio
import logging

from homeassistant.components.device_tracker.const import (
    ATTR_SOURCE_TYPE,
    DOMAIN,
    SOURCE_TYPE_BLUETOOTH_LE,
)

from homeassistant.components.device_tracker.config_entry import ScannerEntity

from homeassistant.const import (
    CONF_DEVICES,
    CONF_NAME,
    CONF_UNIQUE_ID,
    STATE_HOME,
    STATE_NOT_HOME,
)
from homeassistant.helpers import device_registry
from homeassistant.helpers.restore_state import RestoreEntity
import homeassistant.util.dt as dt_util

from .const import (
    CONF_DEVICE_TRACK,
    CONF_PERIOD,
    DOMAIN,
)


_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, conf, add_entities, discovery_info=None):
    """Set up from setup_entry."""
    return True


async def async_setup_entry(hass, config_entry, add_entities):
    """Set up the binary sensor platform."""
    _LOGGER.debug("Starting device tracker entry startup")

    blemonitor = hass.data[DOMAIN]["blemonitor"]
    bleupdater = BLEupdaterTracker(blemonitor, add_entities)
    hass.loop.create_task(bleupdater.async_run(hass))
    _LOGGER.debug("Device Tracker entry setup finished")
    # Return successful setup
    return True


class BLEupdaterTracker():
    """BLE monitor entities updater."""

    def __init__(self, blemonitor, add_entities):
        """Initiate BLE updater."""
        _LOGGER.debug("BLE device tracker updater initialization")
        self.monitor = blemonitor
        self.dataqueue = blemonitor.dataqueue["tracker"].async_q
        self.config = blemonitor.config
        self.period = self.config[CONF_PERIOD]
        self.add_entities = add_entities
        _LOGGER.debug("BLE device tracker updater initialized")

    async def async_run(self, hass):
        """Entities updater loop."""

        async def async_add_device_tracker(mac):
            if mac not in trackers_by_mac:
                tracker_entities = []
                tracker = BleScannerEntity(self.config, mac)
                tracker_entities.insert(0, tracker)
                trackers_by_mac[mac] = tracker_entities
                self.add_entities(tracker_entities)
            else:
                tracker_entities = trackers_by_mac[mac]
            return tracker_entities

        _LOGGER.debug("Device tracker updater loop started!")
        trackers_by_mac = {}
        trackers = []
        adv_cnt = 0
        hpriority = []
        ts_last = dt_util.now()
        ts_now = ts_last
        data = None
        await asyncio.sleep(0)

        # Set up device trackers of configured devices on startup when device tracker is available in device registry
        if self.config[CONF_DEVICES]:
            dev_registry = await device_registry.async_get_registry(hass)
            for device in self.config[CONF_DEVICES]:
                mac = device["mac"]
                if CONF_DEVICE_TRACK in device and device[CONF_DEVICE_TRACK]:
                    # setup device trackers from device registry
                    dev = dev_registry.async_get_device({(DOMAIN, mac)}, set())
                    if dev:
                        mac = mac.replace(":", "")
                        trackers = await async_add_device_tracker(mac)
                    else:
                        pass
                else:
                    pass
        else:
            trackers = []

        # Set up new device trackers when first BLE advertisement is received
        trackers = []
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
            # Process data
            if len(hpriority) > 0:
                for entity in hpriority:
                    if entity.pending_update is True:
                        hpriority.remove(entity)
                        entity.async_schedule_update_ha_state(True)
            if data:
                _LOGGER.debug("Data device tracker received: %s", data)
                adv_cnt += 1
                mac = data["mac"]
                rssi = data["rssi"]
                # Set up new device tracker when first BLE advertisement is received
                trackers = await async_add_device_tracker(mac)

                if data["is connected"] is False:
                    data = None
                    continue

                # schedule an immediate update of remote binary sensors
                if "is connected" in data:
                    entity = trackers[0]
                    entity.collect(data)
                    if entity.pending_update is True:
                        entity.async_schedule_update_ha_state(True)
                    elif entity.ready_for_update is False and entity.enabled is True:
                        hpriority.append(entity)
                data = None
            ts_now = dt_util.now()
            if ts_now - ts_last < timedelta(seconds=self.period):
                continue
            ts_last = ts_now
            _LOGGER.debug(
                "%i BLE ADV messages processed last %i seconds for %i device tracker device(s).",
                adv_cnt,
                self.period,
                len(trackers),
            )
            adv_cnt = 0
        return True


class BleScannerEntity(ScannerEntity, RestoreEntity):
    """Represent a tracked device."""

    def __init__(self, config, mac):
        """Set up BLE Tracker entity."""
        self.ready_for_update = False
        self._config = config
        self._mac = mac
        self._fmac = ":".join(self._mac[i:i + 2] for i in range(0, len(self._mac), 2))
        self._device_settings = self.get_device_settings()
        self._device_name = self._device_settings["name"]
        self._name = "ble tracker {}".format(self._device_name)
        self._state = None
        self._is_connected = None
        self._extra_state_attributes = {}
        self._unique_id = "ble_tracker_" + self._device_name
        self._measurement = "is connected"
        self._newstate = None

    async def async_added_to_hass(self):
        """Handle entity which will be added."""
        _LOGGER.debug("async_added_to_hass called for %s", self.name)
        await super().async_added_to_hass()
        # Restore the old state if available
        # if self._restore_state is False:
        #    self.ready_for_update = True
        #    return
        old_state = await self.async_get_last_state()
        if not old_state:
            self.ready_for_update = True
            return
        self._state = None
        if old_state.state == STATE_HOME:
            self._state = STATE_HOME
        elif old_state.state == STATE_NOT_HOME:
            self._state = STATE_NOT_HOME
        if "rssi" in old_state.attributes:
            self._extra_state_attributes["rssi"] = old_state.attributes["rssi"]
        self.ready_for_update = True

    @property
    def is_connected(self):
        """Return the connection state of the device."""
        return self._is_connected if self._is_connected is not None else None

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device tracker."""
        if self.is_connected is None:
            return None
        return STATE_HOME if self.is_connected else STATE_NOT_HOME

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._extra_state_attributes

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._unique_id

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SOURCE_TYPE_BLUETOOTH_LE

    @property
    def mac_address(self):
        """Return the mac address of the device."""
        return self._fmac

    @property
    def device_info(self):
        """Return device info."""
        return {
            "name": self._device_name,
            "identifiers": {(DOMAIN, self._fmac)}
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
        dev_track = False

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
                    if CONF_DEVICE_TRACK in device:
                        dev_track = device[CONF_DEVICE_TRACK]
        device_settings = {
            "name": dev_name,
            "track device": dev_track,
        }
        _LOGGER.error(
            "Device tracker device with mac address %s has the following settings. "
            "Name: %s. "
            "Track device: %s",
            self._fmac,
            device_settings["name"],
            device_settings["track device"],
        )
        return device_settings

    @property
    def pending_update(self):
        """Check if entity is enabled."""
        return self.enabled and self.ready_for_update

    def collect(self, data):
        """Measurements collector."""
        if self.enabled is False:
            return
        self._newstate = data[self._measurement]
        self._is_connected = self._newstate
        self._extra_state_attributes["rssi"] = data["rssi"]

    async def async_update(self):
        """Update sensor state and attribute."""
        self._state = self._newstate
