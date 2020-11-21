"""Passive BLE monitor integration."""
import logging
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

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
)

_LOGGER = logging.getLogger(__name__)

# regex constants for configuration schema
MAC_REGEX = "(?i)^(?:[0-9A-F]{2}[:]){5}(?:[0-9A-F]{2})$"
AES128KEY_REGEX = "(?i)^[A-F0-9]{32}$"

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


def setup(hass, config):
    """Set up integration."""
    hass.data[DOMAIN] = config[DOMAIN]
    discovery.load_platform(hass, "sensor", DOMAIN, {}, config)
    return True
