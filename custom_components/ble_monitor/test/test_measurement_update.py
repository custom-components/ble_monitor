"""Tests for periodic and instant measurement updates."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from ble_monitor.const import (CONF_DEVICE_MEASUREMENT_UPDATE,
                               CONF_MEASUREMENT_UPDATE,
                               DEFAULT_MEASUREMENT_UPDATE, DOMAIN)
from ble_monitor.sensor import BaseSensor, BLEupdater, MeasuringSensor
from homeassistant.const import CONF_DEVICES

from ble_monitor import CONFIG_SCHEMA


def make_sensor(policy, measurements, rssi_values):
    """Create a minimal measuring entity for update-policy tests."""
    sensor = MeasuringSensor.__new__(MeasuringSensor)
    sensor._measurement_update = policy
    sensor._measurements = list(measurements)
    sensor.rssi_values = list(rssi_values)
    sensor._use_median = False
    sensor._period_cnt = 1
    sensor._extra_state_attributes = {}
    sensor._state = None
    sensor._err = None
    sensor.pending_update = True
    sensor.entity_description = SimpleNamespace(key="temperature", name="Temperature")
    return sensor


def test_configuration_default_and_values():
    """Periodic is the default and both supported policies validate."""
    assert CONFIG_SCHEMA({DOMAIN: {}})[DOMAIN][CONF_MEASUREMENT_UPDATE] == (
        DEFAULT_MEASUREMENT_UPDATE
    )
    for policy in ("periodic", "instant"):
        assert CONFIG_SCHEMA(
            {DOMAIN: {CONF_MEASUREMENT_UPDATE: policy}}
        )[DOMAIN][CONF_MEASUREMENT_UPDATE] == policy


def test_device_override_and_inheritance():
    """A device can override or inherit the global update policy."""
    sensor = BaseSensor.__new__(BaseSensor)
    sensor._key = sensor._fkey = "A4C1380283F4"
    sensor._type = "mac"
    base = {
        CONF_MEASUREMENT_UPDATE: "instant",
        "use_median": False,
        "restore_state": False,
    }
    sensor._config = {**base, CONF_DEVICES: [{"mac": sensor._fkey, CONF_DEVICE_MEASUREMENT_UPDATE: "default"}]}
    assert sensor.get_device_settings()["measurement update"] == "instant"
    sensor._config[CONF_DEVICES][0][CONF_DEVICE_MEASUREMENT_UPDATE] = "periodic"
    assert sensor.get_device_settings()["measurement update"] == "periodic"


def test_instant_uses_latest_raw_value_and_current_rssi_only():
    """Instant updates do not combine values or RSSI between packets."""
    sensor = make_sensor("instant", [17.05], [-73])
    asyncio.run(sensor.async_update())
    assert sensor.native_value == 17.05
    assert sensor._extra_state_attributes["rssi"] == -73
    assert sensor._measurements == []
    assert sensor.rssi_values == []
    for attribute in ("median", "mean", "last_median_of", "last_mean_of"):
        assert attribute not in sensor._extra_state_attributes


def test_instant_removes_restored_aggregation_attributes():
    """Switching to instant mode removes attributes restored from periodic mode."""
    sensor = make_sensor("instant", [17.05], [-73])
    sensor._extra_state_attributes.update(
        {"median": 17.0, "mean": 17.1, "last_median_of": 3, "last_mean_of": 3}
    )
    asyncio.run(sensor.async_update())
    assert sensor._extra_state_attributes == {"rssi": -73}


def test_updater_does_not_write_entity_before_it_is_ready():
    """An unattached entity retains its pending value without a HA state write."""
    entity = SimpleNamespace(
        ready_for_update=False,
        rssi_values=[],
        async_update=AsyncMock(),
        async_write_ha_state=Mock(),
    )
    assert asyncio.run(BLEupdater.async_publish_instant(entity, -73)) is False
    entity.async_update.assert_not_awaited()
    entity.async_write_ha_state.assert_not_called()


def test_updater_writes_ready_entity_immediately():
    """An attached entity receives current RSSI and is written immediately."""
    entity = SimpleNamespace(
        ready_for_update=True,
        rssi_values=[],
        async_update=AsyncMock(),
        async_write_ha_state=Mock(),
    )
    assert asyncio.run(BLEupdater.async_publish_instant(entity, -71)) is True
    assert entity.rssi_values == [-71]
    entity.async_update.assert_awaited_once_with()
    entity.async_write_ha_state.assert_called_once_with()


def test_two_new_packets_produce_two_raw_instant_states():
    """Consecutive accepted packets are never combined in instant mode."""
    sensor = make_sensor("instant", [17.05], [-73])
    asyncio.run(sensor.async_update())
    states = [sensor.native_value]

    sensor._measurements.append(17.06)
    sensor.rssi_values.append(-71)
    asyncio.run(sensor.async_update())
    states.append(sensor.native_value)

    assert states == [17.05, 17.06]


def test_periodic_retains_mean_behavior():
    """Periodic updates retain existing mean aggregation."""
    sensor = make_sensor("periodic", [17.01, 17.05], [-70, -74])
    asyncio.run(sensor.async_update())
    assert sensor.native_value == 17.03
    assert sensor._extra_state_attributes["rssi"] == -72
