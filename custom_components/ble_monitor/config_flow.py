"""Config flow for BLE Monitor."""
import copy
import logging
import re
import voluptuous as vol

from homeassistant.core import callback
from homeassistant import data_entry_flow
from homeassistant.helpers import device_registry, config_validation as cv
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
    DEFAULT_DECIMALS,
    DEFAULT_PERIOD,
    DEFAULT_LOG_SPIKES,
    DEFAULT_USE_MEDIAN,
    DEFAULT_ACTIVE_SCAN,
    DEFAULT_BATT_ENTITIES,
    DEFAULT_REPORT_UNKNOWN,
    DEFAULT_DISCOVERY,
    DEFAULT_RESTORE_STATE,
    DEFAULT_DEVICE_DECIMALS,
    DEFAULT_DEVICE_USE_MEDIAN,
    DEFAULT_DEVICE_RESTORE_STATE,
    DEFAULT_DEVICE_RESET_TIMER,
    CONF_DECIMALS,
    CONF_PERIOD,
    CONF_LOG_SPIKES,
    CONF_USE_MEDIAN,
    CONF_ACTIVE_SCAN,
    CONF_HCI_INTERFACE,
    CONF_BT_INTERFACE,
    CONF_BATT_ENTITIES,
    CONF_REPORT_UNKNOWN,
    CONF_RESTORE_STATE,
    CONF_ENCRYPTION_KEY,
    CONF_DEVICE_DECIMALS,
    CONF_DEVICE_USE_MEDIAN,
    CONF_DEVICE_RESTORE_STATE,
    CONF_DEVICE_RESET_TIMER,
    CONFIG_IS_FLOW,
    DOMAIN,
    MAC_REGEX,
    AES128KEY_REGEX,
)

from . import (
    BT_MAC_INTERFACES,
    DEFAULT_BT_INTERFACE,
)

_LOGGER = logging.getLogger(__name__)


OPTION_LIST_DEVICE = "--Devices--"
OPTION_ADD_DEVICE = "Add device..."
DOMAIN_TITLE = "Bluetooth Low Energy Monitor"


DEVICE_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_MAC, default=""): cv.string,
        vol.Optional(CONF_ENCRYPTION_KEY, default=""): cv.string,
        vol.Optional(CONF_TEMPERATURE_UNIT, default=TEMP_CELSIUS): vol.In(
            [TEMP_CELSIUS, TEMP_FAHRENHEIT]
        ),
        vol.Optional(CONF_DEVICE_DECIMALS, default=DEFAULT_DEVICE_DECIMALS): vol.In(
            [DEFAULT_DEVICE_DECIMALS, 0, 1, 2, 3]
        ),
        vol.Optional(
            CONF_DEVICE_USE_MEDIAN, default=DEFAULT_DEVICE_USE_MEDIAN): vol.In(
            [DEFAULT_DEVICE_USE_MEDIAN, True, False]
        ),
        vol.Optional(
            CONF_DEVICE_RESTORE_STATE, default=DEFAULT_DEVICE_RESTORE_STATE): vol.In(
            [DEFAULT_DEVICE_RESTORE_STATE, True, False]
        ),
        vol.Optional(
            CONF_DEVICE_RESET_TIMER, default=DEFAULT_DEVICE_RESET_TIMER
        ): cv.positive_int,
    }
)

DOMAIN_SCHEMA = vol.Schema(
    {
        vol.Optional(
            CONF_BT_INTERFACE, default=[DEFAULT_BT_INTERFACE]
        ): cv.multi_select(BT_MAC_INTERFACES),
        vol.Optional(CONF_PERIOD, default=DEFAULT_PERIOD): cv.positive_int,
        vol.Optional(CONF_DISCOVERY, default=DEFAULT_DISCOVERY): cv.boolean,
        vol.Optional(CONF_ACTIVE_SCAN, default=DEFAULT_ACTIVE_SCAN): cv.boolean,
        vol.Optional(CONF_REPORT_UNKNOWN, default=DEFAULT_REPORT_UNKNOWN): cv.boolean,
        vol.Optional(CONF_BATT_ENTITIES, default=DEFAULT_BATT_ENTITIES): cv.boolean,
        vol.Optional(CONF_DECIMALS, default=DEFAULT_DECIMALS): cv.positive_int,
        vol.Optional(CONF_LOG_SPIKES, default=DEFAULT_LOG_SPIKES): cv.boolean,
        vol.Optional(CONF_USE_MEDIAN, default=DEFAULT_USE_MEDIAN): cv.boolean,
        vol.Optional(CONF_RESTORE_STATE, default=DEFAULT_RESTORE_STATE): cv.boolean,
        vol.Optional(CONF_DEVICES, default=[]): vol.All(
            cv.ensure_list, [DEVICE_SCHEMA]
        ),
    }
)


class BLEMonitorFlow(data_entry_flow.FlowHandler):
    """BLEMonitor flow."""

    def __init__(self):
        """Initialize flow instance."""
        self._devices = {}
        self._sel_device = {}

    def validate_regex(self, value: str, regex: str):
        """Validate that the value is a string that matches a regex."""
        compiled = re.compile(regex)
        if not compiled.match(value):
            return False
        return True

    def validate_mac(self, value: str, errors: list):
        """Mac validation."""
        if not self.validate_regex(value, MAC_REGEX):
            errors[CONF_MAC] = "invalid_mac"

    def validate_key(self, value: str, errors: list):
        """Key validation."""
        if not value or value == "-":
            return
        if not self.validate_regex(value, AES128KEY_REGEX):
            errors[CONF_ENCRYPTION_KEY] = "invalid_key"

    def _show_main_form(self, errors=None):
        _LOGGER.error("_show_main_form: shouldn't be here")

    def _create_entry(self, uinput):
        _LOGGER.debug("_create_entry: %s", uinput)

        uinput[CONF_DEVICES] = []
        for _, dev in self._devices.items():
            if CONF_ENCRYPTION_KEY in dev and (
                not dev[CONF_ENCRYPTION_KEY] or dev[CONF_ENCRYPTION_KEY] == "-"
            ):
                del dev[CONF_ENCRYPTION_KEY]
            uinput[CONF_DEVICES].append(dev)
        return self.async_create_entry(title=DOMAIN_TITLE, data=uinput)

    @callback
    def _show_user_form(self, step_id=None, schema=None, errors=None):
        option_devices = {}
        option_devices[OPTION_LIST_DEVICE] = OPTION_LIST_DEVICE
        option_devices[OPTION_ADD_DEVICE] = OPTION_ADD_DEVICE
        for _, device in self._devices.items():
            name = (
                device.get(CONF_NAME)
                if device.get(CONF_NAME)
                else device.get(CONF_MAC).upper()
            )
            option_devices[device.get(CONF_MAC).upper()] = name
        config_schema = schema.extend(
            {
                vol.Optional(CONF_DEVICES, default=OPTION_LIST_DEVICE): vol.In(
                    option_devices
                ),
            }
        )
        return self.async_show_form(
            step_id=step_id, data_schema=config_schema, errors=errors or {}
        )

    async def async_step_add_device(self, user_input=None):
        """Add device step."""
        errors = {}
        if user_input is not None:
            _LOGGER.debug("async_step_add_device: %s", user_input)
            if user_input[CONF_MAC] and user_input[CONF_MAC] != "-":
                if (
                    self._sel_device and user_input[CONF_MAC].upper() != self._sel_device.get(CONF_MAC).upper()
                ):
                    errors[CONF_MAC] = "cannot_change_mac"
                    user_input[CONF_MAC] = self._sel_device.get(CONF_MAC)
                else:
                    self.validate_mac(user_input[CONF_MAC], errors)
                    self.validate_key(user_input[CONF_ENCRYPTION_KEY], errors)
                if not errors:
                    # updating device configuration instead of overwriting
                    try:
                        self._devices[user_input["mac"].upper()].update(
                            copy.deepcopy(user_input)
                        )
                    except KeyError:
                        self._devices.update(
                            {user_input["mac"].upper(): copy.deepcopy(user_input)}
                        )
                    self._sel_device = {}  # prevent deletion
            if errors:
                retry_device_option_schema = vol.Schema(
                    {
                        vol.Optional(CONF_MAC, default=user_input[CONF_MAC]): str,
                        vol.Optional(
                            CONF_ENCRYPTION_KEY, default=user_input[CONF_ENCRYPTION_KEY]
                        ): str,
                        vol.Optional(
                            CONF_TEMPERATURE_UNIT,
                            default=user_input[CONF_TEMPERATURE_UNIT],
                        ): vol.In([TEMP_CELSIUS, TEMP_FAHRENHEIT]),
                        vol.Optional(
                            CONF_DEVICE_DECIMALS,
                            default=user_input[CONF_DEVICE_DECIMALS],
                        ): vol.In([DEFAULT_DEVICE_DECIMALS, 0, 1, 2, 3]),
                        vol.Optional(
                            CONF_DEVICE_USE_MEDIAN,
                            default=user_input[CONF_DEVICE_USE_MEDIAN],
                        ): vol.In([DEFAULT_DEVICE_USE_MEDIAN, True, False]),
                        vol.Optional(
                            CONF_DEVICE_RESTORE_STATE,
                            default=user_input[CONF_DEVICE_RESTORE_STATE],
                        ): vol.In([DEFAULT_DEVICE_RESTORE_STATE, True, False]),
                        vol.Optional(
                            CONF_DEVICE_RESET_TIMER,
                            default=user_input[CONF_DEVICE_RESET_TIMER],
                        ): cv.positive_int,
                    }
                )
                return self.async_show_form(
                    step_id="add_device",
                    data_schema=retry_device_option_schema,
                    errors=errors,
                )
            if self._sel_device:
                del self._devices[self._sel_device.get(CONF_MAC).upper()]
            return self._show_main_form(errors)
        device_option_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_MAC,
                    default=self._sel_device.get(CONF_MAC)
                    if self._sel_device.get(CONF_MAC)
                    else "",
                ): str,
                vol.Optional(
                    CONF_ENCRYPTION_KEY,
                    default=self._sel_device.get(CONF_ENCRYPTION_KEY)
                    if self._sel_device.get(CONF_ENCRYPTION_KEY)
                    else "",
                ): str,
                vol.Optional(
                    CONF_TEMPERATURE_UNIT,
                    default=self._sel_device.get(CONF_TEMPERATURE_UNIT)
                    if self._sel_device.get(CONF_TEMPERATURE_UNIT)
                    else TEMP_CELSIUS,
                ): vol.In([TEMP_CELSIUS, TEMP_FAHRENHEIT]),
                vol.Optional(
                    CONF_DEVICE_DECIMALS,
                    default=self._sel_device.get(CONF_DEVICE_DECIMALS)
                    if self._sel_device.get(CONF_DEVICE_DECIMALS)
                    else DEFAULT_DEVICE_DECIMALS,
                ): vol.In([DEFAULT_DEVICE_DECIMALS, 0, 1, 2, 3]),
                vol.Optional(
                    CONF_DEVICE_USE_MEDIAN,
                    default=self._sel_device.get(CONF_DEVICE_USE_MEDIAN)
                    if isinstance(self._sel_device.get(CONF_DEVICE_USE_MEDIAN), bool)
                    else DEFAULT_DEVICE_USE_MEDIAN,
                ): vol.In([DEFAULT_DEVICE_USE_MEDIAN, True, False]),
                vol.Optional(
                    CONF_DEVICE_RESTORE_STATE,
                    default=self._sel_device.get(CONF_DEVICE_RESTORE_STATE)
                    if isinstance(self._sel_device.get(CONF_DEVICE_RESTORE_STATE), bool)
                    else DEFAULT_DEVICE_RESTORE_STATE,
                ): vol.In([DEFAULT_DEVICE_RESTORE_STATE, True, False]),
                vol.Optional(
                    CONF_DEVICE_RESET_TIMER,
                    default=self._sel_device.get(CONF_DEVICE_RESET_TIMER)
                    if self._sel_device.get(CONF_DEVICE_RESET_TIMER)
                    else DEFAULT_DEVICE_RESET_TIMER
                ): cv.positive_int,
            }
        )

        return self.async_show_form(
            step_id="add_device",
            data_schema=device_option_schema,
            errors=errors,
        )


class BLEMonitorConfigFlow(BLEMonitorFlow, config_entries.ConfigFlow, domain=DOMAIN):
    """BLEMonitor config flow."""

    VERSION = 2
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return BLEMonitorOptionsFlow(config_entry)

    def _show_main_form(self, errors=None):
        return self._show_user_form("user", DOMAIN_SCHEMA, errors or {})

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        _LOGGER.debug("async_step_user: %s", user_input)
        errors = {}
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if self.hass.data.get(DOMAIN):
            return self.async_abort(reason="single_instance_allowed")
        if user_input is not None:
            if CONF_DEVICES not in user_input:
                user_input[CONF_DEVICES] = {}
            elif user_input[CONF_DEVICES] == OPTION_ADD_DEVICE:
                self._sel_device = {}
                return await self.async_step_add_device()
            if user_input[CONF_DEVICES] in self._devices:
                self._sel_device = self._devices[user_input[CONF_DEVICES]]
                return await self.async_step_add_device()
            await self.async_set_unique_id(DOMAIN_TITLE)
            self._abort_if_unique_id_configured()
            return self._create_entry(user_input)
        return self._show_main_form(errors)

    async def async_step_import(self, user_input=None):
        """Handle import."""
        _LOGGER.debug("async_step_import: %s", user_input)

        user_input[CONF_DEVICES] = OPTION_LIST_DEVICE
        return await self.async_step_user(user_input)


class BLEMonitorOptionsFlow(BLEMonitorFlow, config_entries.OptionsFlow):
    """Handle BLE Monitor options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        super().__init__()
        self.config_entry = config_entry

    def _show_main_form(self, errors=None):
        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_BT_INTERFACE,
                    default=self.config_entry.options.get(
                        CONF_BT_INTERFACE, DEFAULT_BT_INTERFACE
                    ),
                ): cv.multi_select(BT_MAC_INTERFACES),
                vol.Optional(
                    CONF_PERIOD,
                    default=self.config_entry.options.get(
                        CONF_PERIOD, DEFAULT_PERIOD
                    ),
                ): cv.positive_int,
                vol.Optional(
                    CONF_DISCOVERY,
                    default=self.config_entry.options.get(
                        CONF_DISCOVERY, DEFAULT_DISCOVERY
                    ),
                ): cv.boolean,
                vol.Optional(
                    CONF_ACTIVE_SCAN,
                    default=self.config_entry.options.get(
                        CONF_ACTIVE_SCAN, DEFAULT_ACTIVE_SCAN
                    ),
                ): cv.boolean,
                vol.Optional(
                    CONF_REPORT_UNKNOWN,
                    default=self.config_entry.options.get(
                        CONF_REPORT_UNKNOWN, DEFAULT_REPORT_UNKNOWN
                    ),
                ): cv.boolean,
                vol.Optional(
                    CONF_BATT_ENTITIES,
                    default=self.config_entry.options.get(
                        CONF_BATT_ENTITIES, DEFAULT_BATT_ENTITIES
                    ),
                ): cv.boolean,
                vol.Optional(
                    CONF_DECIMALS,
                    default=self.config_entry.options.get(
                        CONF_DECIMALS, DEFAULT_DECIMALS
                    ),
                ): cv.positive_int,
                vol.Optional(
                    CONF_LOG_SPIKES,
                    default=self.config_entry.options.get(
                        CONF_LOG_SPIKES, DEFAULT_LOG_SPIKES
                    ),
                ): cv.boolean,
                vol.Optional(
                    CONF_USE_MEDIAN,
                    default=self.config_entry.options.get(
                        CONF_USE_MEDIAN, DEFAULT_USE_MEDIAN
                    ),
                ): cv.boolean,
                vol.Optional(
                    CONF_RESTORE_STATE,
                    default=self.config_entry.options.get(
                        CONF_RESTORE_STATE, DEFAULT_RESTORE_STATE
                    ),
                ): cv.boolean,
            }
        )
        return self._show_user_form("init", options_schema, errors or {})

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        _LOGGER.debug("async_step_init user_input: %s", user_input)

        if user_input is not None:
            _LOGGER.debug("async_step_init (after): %s", user_input)
            if (
                CONFIG_IS_FLOW in self.config_entry.options and not self.config_entry.options[CONFIG_IS_FLOW]
            ):
                return self.async_abort(reason="not_in_use")
            if user_input[CONF_DEVICES] == OPTION_ADD_DEVICE:
                self._sel_device = {}
                return await self.async_step_add_device()
            if user_input[CONF_DEVICES] in self._devices:
                self._sel_device = self._devices[user_input[CONF_DEVICES]]
                return await self.async_step_add_device()
            return self._create_entry(user_input)
        _LOGGER.debug("async_step_init (before): %s", self.config_entry.options)

        if (
            CONFIG_IS_FLOW in self.config_entry.options and not self.config_entry.options[CONFIG_IS_FLOW]
        ):
            options_schema = vol.Schema({vol.Optional("not_in_use", default=""): str})
            return self.async_show_form(
                step_id="init", data_schema=options_schema, errors=errors or {}
            )
        for dev in self.config_entry.options.get(CONF_DEVICES):
            self._devices[dev[CONF_MAC].upper()] = dev
        devreg = await self.hass.helpers.device_registry.async_get_registry()
        for dev in device_registry.async_entries_for_config_entry(devreg, self.config_entry.entry_id):
            for iddomain, idmac in dev.identifiers:
                if iddomain != DOMAIN:
                    continue
                name = dev.name_by_user if dev.name_by_user else dev.name
                if idmac in self._devices:
                    self._devices[idmac][CONF_NAME] = name
                else:
                    self._devices[idmac] = {CONF_MAC: idmac, CONF_NAME: name}

        # sort devices by name
        sorteddev_tuples = sorted(self._devices.items(), key=lambda item: item[1].get("name", item[1]["mac"]))
        self._devices = dict(sorteddev_tuples)
        self.hass.config_entries.async_update_entry(
            self.config_entry, unique_id=self.config_entry.entry_id
        )
        return self._show_main_form(errors)
