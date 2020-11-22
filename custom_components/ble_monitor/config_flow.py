"""Config flow for BLE Monitor."""
import logging
import voluptuous as vol

from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant import config_entries
from homeassistant.const import (
    CONF_DEVICES,
    CONF_DISCOVERY,
    CONF_MAC,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
)

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

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_MAC): cv.matches_regex(MAC_REGEX),
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_ENCRYPTION_KEY): cv.matches_regex(AES128KEY_REGEX),
        vol.Optional(CONF_TEMPERATURE_UNIT): cv.temperature_unit,
    }
)

DOMAIN_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ROUNDING, default=DEFAULT_ROUNDING): cv.boolean,
        vol.Optional(CONF_DECIMALS, default=DEFAULT_DECIMALS): cv.positive_int,
        vol.Optional(CONF_PERIOD, default=DEFAULT_PERIOD): cv.positive_int,
        vol.Optional(CONF_LOG_SPIKES, default=DEFAULT_LOG_SPIKES): cv.boolean,
        vol.Optional(CONF_USE_MEDIAN, default=DEFAULT_USE_MEDIAN): cv.boolean,
        vol.Optional(CONF_ACTIVE_SCAN, default=DEFAULT_ACTIVE_SCAN): cv.boolean,
        # vol.Optional(
        #     CONF_HCI_INTERFACE, default=[DEFAULT_HCI_INTERFACE]
        # ): vol.All(cv.ensure_list, [cv.positive_int]),
        vol.Optional(
            CONF_BATT_ENTITIES, default=DEFAULT_BATT_ENTITIES
        ): cv.boolean,
        vol.Optional(
            CONF_REPORT_UNKNOWN, default=DEFAULT_REPORT_UNKNOWN
        ): cv.boolean,
        vol.Optional(CONF_DISCOVERY, default=DEFAULT_DISCOVERY): cv.boolean,
        vol.Optional(CONF_RESTORE_STATE, default=DEFAULT_RESTORE_STATE): cv.boolean,
        # vol.Optional(CONF_DEVICES, default=[]): vol.All(
        #     cv.ensure_list, [DEVICE_SCHEMA]
        # ),
    }
)

_LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register(DOMAIN)
class BLEMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return BLEMonitorOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        _LOGGER.info("async_step_user")
        errors = {}
        if user_input is not None:
            title = f"BLE Monitor"
            await self.async_set_unique_id(title)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=title, data=user_input)

        return self._show_user_form(errors)

    async def async_step_import(self, user_input=None):
        """Handle import."""
        _LOGGER.info("async_step_import: %s", user_input)
        return await self.async_step_user(user_input)

    @callback
    def _show_user_form(self, errors=None):
        return self.async_show_form(
            step_id="user", data_schema=DOMAIN_SCHEMA, errors=errors or {}
        )

class BLEMonitorOptionsFlow(config_entries.OptionsFlow):
    """Handle SpeedTest options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            _LOGGER.info("async_step_init: %s", user_input)
            return self.async_create_entry(title="", data=user_input)

        _LOGGER.info("async_step_init: %s", self.config_entry.options)
        options_schema = vol.Schema(
            {
                vol.Optional(CONF_ROUNDING, default=self.config_entry.options.get(CONF_ROUNDING, DEFAULT_ROUNDING)): cv.boolean,
                vol.Optional(CONF_DECIMALS, default=self.config_entry.options.get(CONF_DECIMALS, DEFAULT_DECIMALS)): cv.positive_int,
                vol.Optional(CONF_PERIOD, default=self.config_entry.options.get(CONF_PERIOD, DEFAULT_PERIOD)): cv.positive_int,
                vol.Optional(CONF_LOG_SPIKES, default=self.config_entry.options.get(CONF_LOG_SPIKES, DEFAULT_LOG_SPIKES)): cv.boolean,
                vol.Optional(CONF_USE_MEDIAN, default=self.config_entry.options.get(CONF_USE_MEDIAN, DEFAULT_USE_MEDIAN)): cv.boolean,
                vol.Optional(CONF_ACTIVE_SCAN, default=self.config_entry.options.get(CONF_ACTIVE_SCAN, DEFAULT_ACTIVE_SCAN)): cv.boolean,
                # vol.Optional(
                #     CONF_HCI_INTERFACE, default=[DEFAULT_HCI_INTERFACE]
                # ): vol.All(cv.ensure_list, [cv.positive_int]),
                vol.Optional(
                    CONF_BATT_ENTITIES, default=self.config_entry.options.get(CONF_BATT_ENTITIES, DEFAULT_BATT_ENTITIES)
                ): cv.boolean,
                vol.Optional(
                    CONF_REPORT_UNKNOWN, default=self.config_entry.options.get(CONF_REPORT_UNKNOWN, DEFAULT_REPORT_UNKNOWN)
                ): cv.boolean,
                vol.Optional(CONF_DISCOVERY, default=self.config_entry.options.get(CONF_DISCOVERY, DEFAULT_DISCOVERY)): cv.boolean,
                vol.Optional(CONF_RESTORE_STATE, default=self.config_entry.options.get(CONF_RESTORE_STATE, DEFAULT_RESTORE_STATE)): cv.boolean,
                # vol.Optional(CONF_DEVICES, default=[]): vol.All(
                #     cv.ensure_list, [DEVICE_SCHEMA]
                # ),
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )
