"""Tests for BLE Monitor device registry lookups."""

from ble_monitor.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from pytest_homeassistant.common import MockConfigEntry, async_capture_events


async def test_identifier_lookup_is_scoped_to_config_entry(
    hass: HomeAssistant, device_registry: dr.DeviceRegistry
) -> None:
    """An identifier lookup selects only the BLE Monitor entry's device."""
    registry = device_registry
    ble_entry = MockConfigEntry(domain=DOMAIN)
    other_entry = MockConfigEntry(domain=DOMAIN)
    ble_entry.add_to_hass(hass)
    other_entry.add_to_hass(hass)
    ble_entry_id = ble_entry.entry_id
    other_entry_id = other_entry.entry_id
    identifier = (DOMAIN, "A4C138000001")
    ble_device = registry.async_get_or_create(
        config_entry_id=ble_entry_id,
        identifiers={identifier},
        name="BLE Monitor device",
    )
    other_device = registry.async_get_or_create(
        config_entry_id=other_entry_id,
        identifiers={identifier},
        name="Other config entry device",
    )
    events = async_capture_events(hass, dr.EVENT_DEVICE_REGISTRY_UPDATED)

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
    await hass.async_block_till_done()
    assert len(events) == 1
    assert events[0].data["action"] == "remove"
    assert events[0].data["device_id"] == ble_device.id
