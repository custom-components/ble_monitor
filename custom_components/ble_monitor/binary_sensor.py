"""Passive BLE monitor sensor platform."""
from datetime import timedelta
import logging
import queue
from threading import Thread

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_LIGHT,
    DEVICE_CLASS_OPENING,
    DEVICE_CLASS_POWER,
    BinarySensorEntity,
)
from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.helpers.restore_state import RestoreEntity
import homeassistant.util.dt as dt_util

from . import (
    CONF_DEVICES,
    CONF_PERIOD,
    CONF_BATT_ENTITIES,
    CONF_RESTORE_STATE,
)
from .const import (
    DOMAIN,
    MMTS_DICT,
)

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, conf, add_entities, discovery_info=None):
    """Set up the binary_sensor platform."""
    _LOGGER.debug("Binary sensor platform setup")
    blemonitor = hass.data[DOMAIN]
    bleupdater = BLEupdaterBinary(blemonitor, add_entities)
    bleupdater.start()
    _LOGGER.debug("Binary sensor platform setup finished")
    # Return successful setup
    return True


class BLEupdaterBinary(Thread):
    """BLE monitor entities updater."""

    def __init__(self, blemonitor, add_entities):
        """Initiate BLE updater."""
        Thread.__init__(self, daemon=True)
        _LOGGER.debug("BLE binary sensors updater initialization")
        self.monitor = blemonitor
        self.dataqueue = blemonitor.dataqueue["binary"]
        self.config = blemonitor.config
        self.period = self.config[CONF_PERIOD]
        self.batt_entities = self.config[CONF_BATT_ENTITIES]
        self.add_entities = add_entities
        _LOGGER.debug("BLE binary sensors updater initialized")

    def run(self):
        """Entities updater loop."""

        _LOGGER.debug("Binary entities updater loop started!")
        sensors_by_mac = {}
        sensors = []
        batt = {}  # batteries
        mibeacon_cnt = 0
        hpriority = []
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
            if len(hpriority) > 0:
                for entity in hpriority:
                    if entity.pending_update is True:
                        hpriority.remove(entity)
                        entity.schedule_update_ha_state(True)
            if data:
                mibeacon_cnt += 1
                mac = data["mac"]
                batt_attr = None
                sensortype = data["type"]
                sw_i, op_i, l_i, b_i = MMTS_DICT[sensortype][1]
                if mac not in sensors_by_mac:
                    sensors = []
                    if sw_i != 9:
                        sensors.insert(sw_i, PowerBinarySensor(self.config, mac, sensortype))
                    if op_i != 9:
                        sensors.insert(op_i, OpeningBinarySensor(self.config, mac, sensortype))
                    if l_i != 9:
                        sensors.insert(l_i, LightBinarySensor(self.config, mac, sensortype))
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
                        for entity in sensors:
                            getattr(entity, "_device_state_attributes")[ATTR_BATTERY_LEVEL] = batt_attr
                            if entity.pending_update is True:
                                entity.schedule_update_ha_state(False)
                    else:
                        try:
                            batt_attr = batt[mac]
                        except KeyError:
                            batt_attr = None
                # schedule an immediate update of binary sensors
                if "switch" in data:
                    switch = sensors[sw_i]
                    switch.collect(data, batt_attr)
                    if switch.pending_update is True:
                        switch.schedule_update_ha_state(True)
                    elif switch.ready_for_update is False and switch.enabled is True:
                        hpriority.append(switch)
                if "opening" in data:
                    opening = sensors[op_i]
                    opening.collect(data, batt_attr)
                    if opening.pending_update is True:
                        opening.schedule_update_ha_state(True)
                    elif opening.ready_for_update is False and opening.enabled is True:
                        hpriority.append(opening)
                if "light" in data:
                    light = sensors[l_i]
                    light.collect(data, batt_attr)
                    if light.pending_update is True:
                        light.schedule_update_ha_state(True)
                    elif light.ready_for_update is False and light.enabled is True:
                        hpriority.append(light)
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


class SwitchingSensor(RestoreEntity, BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        self.ready_for_update = False
        self._sensor_name = ""
        self._mac = mac
        self._config = config
        self._restore_state = config[CONF_RESTORE_STATE]
        self._name = ""
        self._state = None
        self._unique_id = ""
        self._device_type = devtype
        self._device_state_attributes = {}
        self._device_state_attributes["sensor type"] = devtype
        self._device_state_attributes["mac address"] = (
            ':'.join(mac[i:i + 2] for i in range(0, len(mac), 2))
        )
        self._device_class = None
        self._newstate = None
        self._measurement = "measurement"

    async def async_added_to_hass(self):
        """Handle entity which will be added."""
        _LOGGER.debug("async_added_to_hass called for %s", self.name)
        await super().async_added_to_hass()
        # Restore the old state if available
        if self._restore_state is False:
            self.ready_for_update = True
            return
        old_state = await self.async_get_last_state()
        _LOGGER.debug(old_state)
        if not old_state:
            self.ready_for_update = True
            return
        self._state = True if old_state.state == STATE_ON else False
        if "ext_state" in old_state.attributes:
            self._device_state_attributes["ext_state"] = old_state.attributes["ext_state"]
        if "rssi" in old_state.attributes:
            self._device_state_attributes["rssi"] = old_state.attributes["rssi"]
        if "last packet id" in old_state.attributes:
            self._device_state_attributes["last packet id"] = old_state.attributes["last packet id"]
        if ATTR_BATTERY_LEVEL in old_state.attributes:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = old_state.attributes[ATTR_BATTERY_LEVEL]
        self.ready_for_update = True

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return bool(self._state) if self._state is not None else None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the binary sensor."""
        if self.is_on is None:
            return None
        return STATE_ON if self.is_on else STATE_OFF

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._device_state_attributes

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_class(self):
        """Return the device class."""
        return self._device_class

    @property
    def force_update(self):
        """Force update."""
        return True

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

    @property
    def pending_update(self):
        """Checks if entity is enabled"""
        return self.enabled and self.ready_for_update

    def collect(self, data, batt_attr=None):
        """Measurements collector."""
        if self.pending_update is False:
            return
        self._newstate = data[self._measurement]
        self._device_state_attributes["last packet id"] = data["packet"]
        self._device_state_attributes["rssi"] = data["rssi"]
        if batt_attr is not None:
            self._device_state_attributes[ATTR_BATTERY_LEVEL] = batt_attr

    def update(self):
        """Update sensor state and attribute."""
        self._state = self._newstate


class PowerBinarySensor(SwitchingSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "switch"
        self._sensor_name = self.get_sensorname()
        self._name = "ble switch {}".format(self._sensor_name)
        self._unique_id = "sw_" + self._sensor_name
        self._device_class = DEVICE_CLASS_POWER


class LightBinarySensor(SwitchingSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "light"
        self._sensor_name = self.get_sensorname()
        self._name = "ble light {}".format(self._sensor_name)
        self._unique_id = "lt_" + self._sensor_name
        self._device_class = DEVICE_CLASS_LIGHT


class OpeningBinarySensor(SwitchingSensor):
    """Representation of a Sensor."""

    def __init__(self, config, mac, devtype):
        """Initialize the sensor."""
        super().__init__(config, mac, devtype)
        self._measurement = "opening"
        self._sensor_name = self.get_sensorname()
        self._name = "ble opening {}".format(self._sensor_name)
        self._unique_id = "op_" + self._sensor_name
        self._ext_state = None
        self._device_class = DEVICE_CLASS_OPENING

    def update(self):
        """Update sensor state and attributes."""
        self._ext_state = self._newstate
        self._state = not bool(self._newstate) if self._ext_state < 2 else bool(self._newstate)
        self._device_state_attributes["ext_state"] = self._ext_state
