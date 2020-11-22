"""Passive BLE monitor integration."""
import logging
import asyncio
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry

from homeassistant.const import (
    CONF_DEVICES,
    CONF_DISCOVERY,
    CONF_MAC,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
)

from homeassistant.helpers import discovery

from .const import (
    DEFAULT_ROUNDING,
    DEFAULT_DECIMALS,
    DEFAULT_PERIOD,
    DEFAULT_LOG_SPIKES,
    DEFAULT_USE_MEDIAN,
    DEFAULT_ACTIVE_SCAN,
    DEFAULT_HCI_INTERFACE,
    DEFAULT_BATT_ENTITIES,
    DEFAULT_REPORT_UNKNOWN,
    DEFAULT_DISCOVERY,
    DEFAULT_RESTORE_STATE,
    CONF_ROUNDING,
    CONF_DECIMALS,
    CONF_PERIOD,
    CONF_LOG_SPIKES,
    CONF_USE_MEDIAN,
    CONF_ACTIVE_SCAN,
    CONF_HCI_INTERFACE,
    CONF_BATT_ENTITIES,
    CONF_REPORT_UNKNOWN,
    CONF_RESTORE_STATE,
    CONF_ENCRYPTION_KEY,
    DOMAIN,
    MAC_REGEX,
    AES128KEY_REGEX,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_MAC): cv.matches_regex(MAC_REGEX),
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_ENCRYPTION_KEY): cv.matches_regex(AES128KEY_REGEX),
        vol.Optional(CONF_TEMPERATURE_UNIT): cv.temperature_unit,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_ROUNDING, default=DEFAULT_ROUNDING): cv.boolean,
                vol.Optional(CONF_DECIMALS, default=DEFAULT_DECIMALS): cv.positive_int,
                vol.Optional(CONF_PERIOD, default=DEFAULT_PERIOD): cv.positive_int,
                vol.Optional(CONF_LOG_SPIKES, default=DEFAULT_LOG_SPIKES): cv.boolean,
                vol.Optional(CONF_USE_MEDIAN, default=DEFAULT_USE_MEDIAN): cv.boolean,
                vol.Optional(CONF_ACTIVE_SCAN, default=DEFAULT_ACTIVE_SCAN): cv.boolean,
                vol.Optional(
                    CONF_HCI_INTERFACE, default=[DEFAULT_HCI_INTERFACE]
                ): vol.All(cv.ensure_list, [cv.positive_int]),
                vol.Optional(
                    CONF_BATT_ENTITIES, default=DEFAULT_BATT_ENTITIES
                ): cv.boolean,
                vol.Optional(
                    CONF_REPORT_UNKNOWN, default=DEFAULT_REPORT_UNKNOWN
                ): cv.boolean,
                vol.Optional(CONF_DISCOVERY, default=DEFAULT_DISCOVERY): cv.boolean,
                vol.Optional(CONF_RESTORE_STATE, default=DEFAULT_RESTORE_STATE): cv.boolean,
                vol.Optional(CONF_DEVICES, default=[]): vol.All(
                    cv.ensure_list, [DEVICE_SCHEMA]
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up integration."""

    if not DOMAIN in config:
        return True

    _LOGGER.info("Initializing BLE Monitor integration")
    hass.async_add_job(hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_IMPORT}, data=config[DOMAIN]
    ))        
    
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up BLE Monitor from a config entry."""
    _LOGGER.info("Initializing BLE Monitor entry")

    if not entry.unique_id:
        hass.config_entries.async_update_entry(entry, unique_id=entry.title)

    if not entry.options:
        options = entry.data
        hass.config_entries.async_update_entry(entry, options=options)

    entry.add_update_listener(_async_update_listener)
        
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )

    return unload_ok

async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
