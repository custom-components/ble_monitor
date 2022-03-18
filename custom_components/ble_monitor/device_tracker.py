"""Passive BLE monitor device tracker platform."""
from datetime import timedelta
import asyncio
import logging

from homeassistant.components.device_tracker.const import (
    SOURCE_TYPE_BLUETOOTH_LE,
)

from homeassistant.components.device_tracker.config_entry import ScannerEntity

from homeassistant.const import (
    CONF_DEVICES,
    CONF_NAME,
    CONF_UNIQUE_ID,
    CONF_MAC,
    STATE_HOME,
    STATE_NOT_HOME,
)

from homeassistant.helpers.event import async_call_later
from homeassistant.helpers import device_registry
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt

from .helper import (
    identifier_normalize,
    identifier_clean,
    detect_conf_type,
    dict_get_or,
)

from .const import (
    CONF_RESTORE_STATE,
    CONF_DEVICE_RESTORE_STATE,
    CONF_DEVICE_TRACK,
    CONF_DEVICE_TRACKER_SCAN_INTERVAL,
    CONF_DEVICE_TRACKER_CONSIDER_HOME,
    CONF_PERIOD,
    CONF_GATEWAY_ID,
    CONF_UUID,
    DEFAULT_DEVICE_TRACK,
    DEFAULT_DEVICE_TRACKER_SCAN_INTERVAL,
    DEFAULT_DEVICE_TRACKER_CONSIDER_HOME,
    DOMAIN,
)

RESTORE_ATTRIBUTES = [
    'rssi',
    CONF_GATEWAY_ID,
    'major',
    'minor',
    'measured_power',
    'cypress_temperature',
    'cypress_humidity'
]


_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, conf, add_entities, discovery_info=None):
    """Set up from setup_entry."""
    return True


async def async_setup_entry(hass, config_entry, add_entities):
    """Set up the device tracker platform."""
    _LOGGER.debug("Starting device tracker entry startup")

    blemonitor = hass.data[DOMAIN]["blemonitor"]
    bleupdater = BLEupdaterTracker(blemonitor, add_entities)
    hass.loop.create_task(bleupdater.async_run(hass))
    _LOGGER.debug("Device Tracker entry setup finished")
    # Return successful setup
    return True


class BLEupdaterTracker:
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

        async def async_add_device_tracker(key):
            if key not in trackers_by_key:
                tracker_entities = []
                tracker = BleScannerEntity(self.config, key)
                tracker_entities.insert(0, tracker)
                trackers_by_key[key] = tracker_entities
                self.add_entities(tracker_entities)
            else:
                tracker_entities = trackers_by_key[key]
            return tracker_entities

        _LOGGER.debug("Device tracker updater loop started!")
        trackers_by_key = {}
        trackers = []
        adv_cnt = 0
        ts_last = dt.now()
        ts_now = ts_last
        data = None
        await asyncio.sleep(0)

        # Set up device trackers of configured devices on startup when device tracker is available in device registry
        if self.config[CONF_DEVICES]:
            dev_registry = await device_registry.async_get_registry(hass)
            for device in self.config[CONF_DEVICES]:
                key = dict_get_or(device)
                if CONF_DEVICE_TRACK in device and device[CONF_DEVICE_TRACK]:
                    # setup device trackers from device registry
                    dev = dev_registry.async_get_device({(DOMAIN, key.upper())}, set())
                    if dev:
                        key = identifier_clean(key)
                        trackers = await async_add_device_tracker(key)
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
            if data:
                _LOGGER.debug("Data device tracker received: %s", data)
                adv_cnt += 1
                key = dict_get_or(data)
                # Set up new device tracker when first BLE advertisement is received
                trackers = await async_add_device_tracker(key)

                if data["is connected"] is False:
                    data = None
                    continue

                # schedule an immediate update of device tracker
                if "is connected" in data:
                    entity = trackers[0]
                    entity.data_update(data)
                    if entity.pending_update is True:
                        try:
                            entity.async_schedule_update_ha_state(True)
                        except AttributeError:
                            continue
                data = None
            ts_now = dt.now()
            if ts_now - ts_last < timedelta(seconds=self.period):
                continue
            ts_last = ts_now
            _LOGGER.debug(
                "%i BLE ADV messages processed last %i seconds for %i device tracker device(s)",
                adv_cnt,
                self.period,
                len(trackers),
            )
            adv_cnt = 0
        return True


class BleScannerEntity(ScannerEntity, RestoreEntity):
    """Represent a tracked device."""

    def __init__(self, config, key):
        """Set up BLE Tracker entity."""
        self.ready_for_update = False
        self._config = config
        self._type = detect_conf_type(key)
        self._key = key
        self._fkey = identifier_normalize(key)
        self._device_settings = self.get_device_settings()
        self._device_name = self._device_settings["name"]
        self._name = "ble tracker {}".format(self._device_name)
        self._state = None
        self._extra_state_attributes = {}
        self._unique_id = "ble_tracker_" + self._device_name
        self._restore_state = self._device_settings["restore state"]
        self._scan_interval = self._device_settings["scan interval"]
        self._consider_home = self._device_settings["consider home"]
        self._newstate = None
        self._last_seen = None

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
        if "last_seen" in old_state.attributes:
            self._last_seen = dt.parse_datetime(old_state.attributes["last_seen"])
            self._extra_state_attributes["last_seen"] = dt.parse_datetime(
                old_state.attributes["last_seen"]
            )

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
    def is_connected(self):
        """Return the connection state of the device."""
        return self._last_seen and (dt.now() - self._last_seen) < timedelta(
            seconds=self._consider_home
        )

    @property
    def state(self):
        """Return the state of the device."""
        return STATE_HOME if self.is_connected else STATE_NOT_HOME

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def force_update(self):
        """Force update."""
        return True

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
        if not self.is_beacon:
            return self._fkey

        if 'mac_address' in self._extra_state_attributes:
            return self._extra_state_attributes['mac_address']

        return None

    @property
    def device_info(self):
        """Return device info."""
        return {"name": self._device_name, "identifiers": {(DOMAIN, self._fkey.upper())}}

    def get_device_settings(self):
        """Set device settings."""
        device_settings = {}

        # initial setup of device settings equal to integration settings
        dev_name = self._key
        dev_restore_state = self._config[CONF_RESTORE_STATE]
        dev_track = DEFAULT_DEVICE_TRACK
        dev_scan_interval = DEFAULT_DEVICE_TRACKER_SCAN_INTERVAL
        dev_consider_home = DEFAULT_DEVICE_TRACKER_CONSIDER_HOME

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
                    if CONF_DEVICE_TRACK in device:
                        dev_track = device[CONF_DEVICE_TRACK]
                    if CONF_DEVICE_TRACKER_SCAN_INTERVAL in device:
                        dev_scan_interval = device[CONF_DEVICE_TRACKER_SCAN_INTERVAL]
                    if CONF_DEVICE_TRACKER_CONSIDER_HOME in device:
                        dev_consider_home = device[CONF_DEVICE_TRACKER_CONSIDER_HOME]
        device_settings = {
            "name": dev_name,
            "restore state": dev_restore_state,
            "track device": dev_track,
            "scan interval": dev_scan_interval,
            "consider home": dev_consider_home,
        }
        _LOGGER.debug(
            "Device tracker device with %s %s has the following settings. Name: %s. Restore state: %s. Track device: %s. Scan interval: %s. Consider home interval: %s. ",
            'uuid' if self.is_beacon else 'mac address',
            self._fkey,
            device_settings["name"],
            device_settings["restore state"],
            device_settings["track device"],
            device_settings["scan interval"],
            device_settings["consider home"],
        )
        return device_settings

    @property
    def pending_update(self):
        """Check if entity is enabled."""
        return self.enabled and self.ready_for_update

    def data_update(self, data):
        """Prepare data for update."""
        if self.enabled is False:
            return

        now = dt.now()
        # Do not update within scan interval to save resources
        if self._last_seen:
            if now - self._last_seen <= timedelta(seconds=self._scan_interval):
                self.ready_for_update = False
                return
        self._last_seen = now
        self._extra_state_attributes["last_seen"] = self._last_seen
        restore_attr = RESTORE_ATTRIBUTES
        restore_attr.append('mac_address' if self.is_beacon else 'uuid')

        for attr in restore_attr:
            key = CONF_MAC if attr == 'mac_address' else attr
            if key in data:
                if attr in ['uuid', 'mac_address']:
                    self._extra_state_attributes[attr] = identifier_normalize(data[key])
                    continue

                self._extra_state_attributes[attr] = data[key]

        self.ready_for_update = True

    def recheck_state(self, event=None):
        """Recheck state of the tracker after the consider home interval."""
        self.schedule_update_ha_state(False)

    async def async_update(self):
        """Update tracker state and attribute."""
        self._state = self.state
        async_call_later(self.hass, self._consider_home, self.recheck_state)
