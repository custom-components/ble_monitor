"""Tests for BLE Monitor device registry lookups."""

from unittest.mock import Mock

from ble_monitor.const import DOMAIN
from homeassistant.helpers import device_registry as dr


def test_identifier_lookup_is_scoped_to_config_entry():
    """An identifier lookup selects only the BLE Monitor entry's device."""
    hass = Mock()
    hass.config_entries.async_get_entry.return_value = Mock(domain=DOMAIN)
    registry = object.__new__(dr.DeviceRegistry)
    registry.hass = hass
    registry.devices = dr.ActiveDeviceRegistryItems()
    registry.deleted_devices = dr.DeletedDeviceRegistryItems()
    registry.async_schedule_save = Mock()

    ble_entry_id = "ble-monitor-entry"
    other_entry_id = "other-entry"
    identifier = (DOMAIN, "A4C138000001")
    ble_device = dr.DeviceEntry(
        config_entry_id=ble_entry_id,
        identifiers={identifier},
        name="BLE Monitor device",
    )
    other_device = dr.DeviceEntry(
        config_entry_id=other_entry_id,
        identifiers={identifier},
        name="Other config entry device",
    )
    registry.devices[ble_device.id] = ble_device
    registry.devices[other_device.id] = other_device

    selected = registry.async_get_device_by_identifier(
        identifier, ble_entry_id
    )

    assert selected == ble_device
    assert selected != other_device

    registry.async_remove_device(selected.id)

    assert registry.async_get_device_by_identifier(
        identifier, ble_entry_id
    ) is None
    assert registry.async_get_device_by_identifier(
        identifier, other_entry_id
    ) == other_device
    hass.bus.async_fire_internal.assert_called_once()
