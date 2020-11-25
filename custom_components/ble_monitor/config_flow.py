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
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
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

OPTION_LIST_DEVICE = "--Devices--"
OPTION_ADD_DEVICE = "Add device..."

DOMAIN_SCHEMA = vol.Schema(
    {
        vol.Optional(
            CONF_HCI_INTERFACE, default=[DEFAULT_HCI_INTERFACE]
        ): cv.multi_select({"0": "0", "1": "1", "2": "2"}),
        vol.Optional(CONF_DISCOVERY, default=DEFAULT_DISCOVERY): cv.boolean,
        vol.Optional(CONF_ACTIVE_SCAN, default=DEFAULT_ACTIVE_SCAN): cv.boolean,
        vol.Optional(
            CONF_REPORT_UNKNOWN, default=DEFAULT_REPORT_UNKNOWN
        ): cv.boolean,
        vol.Optional(
            CONF_BATT_ENTITIES, default=DEFAULT_BATT_ENTITIES
        ): cv.boolean,
        vol.Optional(CONF_ROUNDING, default=DEFAULT_ROUNDING): cv.boolean,
        vol.Optional(CONF_DECIMALS, default=DEFAULT_DECIMALS): cv.positive_int,
        vol.Optional(CONF_PERIOD, default=DEFAULT_PERIOD): cv.positive_int,
        vol.Optional(CONF_LOG_SPIKES, default=DEFAULT_LOG_SPIKES): cv.boolean,
        vol.Optional(CONF_USE_MEDIAN, default=DEFAULT_USE_MEDIAN): cv.boolean,
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

    def __init__(self):
        """Initialize flow instance."""
        self._devices = []
        self._sel_device = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return BLEMonitorOptionsFlow(config_entry)

    async def async_step_add_device(self, user_input=None):
        errors = {}
        if user_input is not None:
            if (user_input.get(CONF_MAC)):
                self._devices.append(user_input)
            else:
                for idx in range(0, len(self._devices)-1):
                    if self._devices[idx].get(CONF_MAC) == self._sel_device.get(CONF_MAC):
                        self._devices.pop(idx)
                        break

            return self._show_user_form(errors)

        DEVICE_SCHEMA = vol.Schema(
            {
                vol.Optional(CONF_MAC, default=self._sel_device.get(CONF_MAC) if self._sel_device else ""): cv.string,
                vol.Optional(CONF_NAME, default=self._sel_device.get(CONF_NAME) if self._sel_device else ""): cv.string,
                vol.Optional(CONF_ENCRYPTION_KEY, default=self._sel_device.get(CONF_ENCRYPTION_KEY) if self._sel_device else ""): cv.string,
                vol.Optional(CONF_TEMPERATURE_UNIT, default=self._sel_device.get(CONF_TEMPERATURE_UNIT) if self._sel_device else TEMP_CELSIUS): vol.In([TEMP_CELSIUS, TEMP_FAHRENHEIT]),
            }
        )

        return self.async_show_form(
            step_id="add_device",
            data_schema=DEVICE_SCHEMA,
        )

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        _LOGGER.info("async_step_user")
        errors = {}
        if user_input is not None:
            if user_input[CONF_DEVICES] == OPTION_ADD_DEVICE:
                self._sel_device = {}
                return await self.async_step_add_device()
            for dev in self._devices:
                if dev.get(CONF_MAC) == user_input[CONF_DEVICES]:
                    self._sel_device = dev
                    return await self.async_step_add_device()

            title = f"BLE Monitor"
            await self.async_set_unique_id(title)
            self._abort_if_unique_id_configured()
            user_input[CONF_DEVICES] = self._devices

            return self.async_create_entry(title=title, data=user_input)

        return self._show_user_form(errors)

    async def async_step_import(self, user_input=None):
        """Handle import."""
        _LOGGER.info("async_step_import: %s", user_input)
        return await self.async_step_user(user_input)

    @callback
    def _show_user_form(self, errors=None):
        option_devices = []
        option_devices.append(OPTION_LIST_DEVICE)
        option_devices.append(OPTION_ADD_DEVICE)
        for device in self._devices:
            option_devices.append(device.get(CONF_MAC));
        config_schema = DOMAIN_SCHEMA.extend({
            vol.Optional(CONF_DEVICES, default=OPTION_LIST_DEVICE): vol.In(option_devices),
        })
        return self.async_show_form(
            step_id="user", data_schema=config_schema, errors=errors or {}
        )

class BLEMonitorOptionsFlow(config_entries.OptionsFlow):
    """Handle BLE Monitor options."""

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
                vol.Optional(
                    CONF_HCI_INTERFACE, default=self.config_entry.options.get(CONF_HCI_INTERFACE, DEFAULT_HCI_INTERFACE)
                ): cv.multi_select({"0": "0", "1": "1", "2": "2"}),
                vol.Optional(CONF_DISCOVERY, default=self.config_entry.options.get(CONF_DISCOVERY, DEFAULT_DISCOVERY)): cv.boolean,
                vol.Optional(CONF_ACTIVE_SCAN, default=self.config_entry.options.get(CONF_ACTIVE_SCAN, DEFAULT_ACTIVE_SCAN)): cv.boolean,
                vol.Optional(
                    CONF_REPORT_UNKNOWN, default=self.config_entry.options.get(CONF_REPORT_UNKNOWN, DEFAULT_REPORT_UNKNOWN)
                ): cv.boolean,
                vol.Optional(
                    CONF_BATT_ENTITIES, default=self.config_entry.options.get(CONF_BATT_ENTITIES, DEFAULT_BATT_ENTITIES)
                ): cv.boolean,
                vol.Optional(CONF_ROUNDING, default=self.config_entry.options.get(CONF_ROUNDING, DEFAULT_ROUNDING)): cv.boolean,
                vol.Optional(CONF_DECIMALS, default=self.config_entry.options.get(CONF_DECIMALS, DEFAULT_DECIMALS)): cv.positive_int,
                vol.Optional(CONF_PERIOD, default=self.config_entry.options.get(CONF_PERIOD, DEFAULT_PERIOD)): cv.positive_int,
                vol.Optional(CONF_LOG_SPIKES, default=self.config_entry.options.get(CONF_LOG_SPIKES, DEFAULT_LOG_SPIKES)): cv.boolean,
                vol.Optional(CONF_USE_MEDIAN, default=self.config_entry.options.get(CONF_USE_MEDIAN, DEFAULT_USE_MEDIAN)): cv.boolean,
                vol.Optional(CONF_RESTORE_STATE, default=self.config_entry.options.get(CONF_RESTORE_STATE, DEFAULT_RESTORE_STATE)): cv.boolean,
                # vol.Optional(CONF_DEVICES, default=[]): vol.All(
                #     cv.ensure_list, [DEVICE_SCHEMA]
                # ),
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )
