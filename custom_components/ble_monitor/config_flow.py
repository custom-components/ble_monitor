"""Config flow for BLE Monitor."""
import copy
import logging
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

from .helper import (
    detect_conf_type,
    dict_get_key_or,
    dict_get_or,
    validate_mac,
    validate_uuid,
    validate_key,
)

from .const import (
    CONF_ACTIVE_SCAN,
    CONF_BT_AUTO_RESTART,
    CONF_BT_INTERFACE,
    CONF_DECIMALS,
    CONF_DEVICE_ENCRYPTION_KEY,
    CONF_DEVICE_DECIMALS,
    CONF_DEVICE_USE_MEDIAN,
    CONF_DEVICE_RESTORE_STATE,
    CONF_DEVICE_RESET_TIMER,
    CONF_DEVICE_TRACK,
    CONF_DEVICE_TRACKER_SCAN_INTERVAL,
    CONF_DEVICE_TRACKER_CONSIDER_HOME,
    CONF_DEVICE_DELETE_DEVICE,
    CONF_LOG_SPIKES,
    CONF_PERIOD,
    CONF_REPORT_UNKNOWN,
    CONF_RESTORE_STATE,
    CONF_USE_MEDIAN,
    CONF_UUID,
    CONFIG_IS_FLOW,
    DEFAULT_ACTIVE_SCAN,
    DEFAULT_BT_AUTO_RESTART,
    DEFAULT_DECIMALS,
    DEFAULT_DEVICE_DECIMALS,
    DEFAULT_DEVICE_ENCRYPTION_KEY,
    DEFAULT_DEVICE_MAC,
    DEFAULT_DEVICE_UUID,
    DEFAULT_DEVICE_USE_MEDIAN,
    DEFAULT_DEVICE_RESTORE_STATE,
    DEFAULT_DEVICE_RESET_TIMER,
    DEFAULT_DEVICE_TRACK,
    DEFAULT_DEVICE_TRACKER_SCAN_INTERVAL,
    DEFAULT_DEVICE_TRACKER_CONSIDER_HOME,
    DEFAULT_DEVICE_DELETE_DEVICE,
    DEFAULT_DISCOVERY,
    DEFAULT_LOG_SPIKES,
    DEFAULT_PERIOD,
    DEFAULT_REPORT_UNKNOWN,
    DEFAULT_RESTORE_STATE,
    DEFAULT_USE_MEDIAN,
    DOMAIN,
    REPORT_UNKNOWN_LIST,
)

from . import (
    DEFAULT_BT_INTERFACE,
    BT_MULTI_SELECT,
)

_LOGGER = logging.getLogger(__name__)


OPTION_LIST_DEVICE = "--Devices--"
OPTION_ADD_DEVICE = "Add device..."
DOMAIN_TITLE = "Bluetooth Low Energy Monitor"

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_MAC, default=DEFAULT_DEVICE_MAC): cv.string,
        vol.Optional(CONF_UUID, default=DEFAULT_DEVICE_UUID): cv.string,
        vol.Optional(CONF_DEVICE_ENCRYPTION_KEY, default=DEFAULT_DEVICE_ENCRYPTION_KEY): cv.string,
        vol.Optional(CONF_TEMPERATURE_UNIT, default=TEMP_CELSIUS): vol.In(
            [TEMP_CELSIUS, TEMP_FAHRENHEIT]
        ),
        vol.Optional(CONF_DEVICE_DECIMALS, default=DEFAULT_DEVICE_DECIMALS): vol.In(
            [DEFAULT_DEVICE_DECIMALS, 0, 1, 2, 3]
        ),
        vol.Optional(CONF_DEVICE_USE_MEDIAN, default=DEFAULT_DEVICE_USE_MEDIAN): vol.In(
            [DEFAULT_DEVICE_USE_MEDIAN, True, False]
        ),
        vol.Optional(
            CONF_DEVICE_RESTORE_STATE, default=DEFAULT_DEVICE_RESTORE_STATE
        ): vol.In([DEFAULT_DEVICE_RESTORE_STATE, True, False]),
        vol.Optional(
            CONF_DEVICE_RESET_TIMER, default=DEFAULT_DEVICE_RESET_TIMER
        ): cv.positive_int,
        vol.Optional(CONF_DEVICE_TRACK, default=DEFAULT_DEVICE_TRACK): cv.boolean,
        vol.Optional(
            CONF_DEVICE_TRACKER_SCAN_INTERVAL,
            default=DEFAULT_DEVICE_TRACKER_SCAN_INTERVAL,
        ): cv.positive_int,
        vol.Optional(
            CONF_DEVICE_TRACKER_CONSIDER_HOME,
            default=DEFAULT_DEVICE_TRACKER_CONSIDER_HOME,
        ): cv.positive_int,
        vol.Optional(
            CONF_DEVICE_DELETE_DEVICE,
            default=DEFAULT_DEVICE_DELETE_DEVICE,
        ): cv.boolean,
    }
)

DOMAIN_SCHEMA = vol.Schema(
    {
        vol.Optional(
            CONF_BT_INTERFACE, default=[DEFAULT_BT_INTERFACE]
        ): cv.multi_select(BT_MULTI_SELECT),
        vol.Optional(CONF_BT_AUTO_RESTART, default=DEFAULT_BT_AUTO_RESTART): cv.boolean,
        vol.Optional(CONF_ACTIVE_SCAN, default=DEFAULT_ACTIVE_SCAN): cv.boolean,
        vol.Optional(CONF_DISCOVERY, default=DEFAULT_DISCOVERY): cv.boolean,
        vol.Optional(CONF_USE_MEDIAN, default=DEFAULT_USE_MEDIAN): cv.boolean,
        vol.Optional(CONF_PERIOD, default=DEFAULT_PERIOD): cv.positive_int,
        vol.Optional(CONF_DECIMALS, default=DEFAULT_DECIMALS): cv.positive_int,
        vol.Optional(CONF_LOG_SPIKES, default=DEFAULT_LOG_SPIKES): cv.boolean,
        vol.Optional(CONF_RESTORE_STATE, default=DEFAULT_RESTORE_STATE): cv.boolean,
        vol.Optional(CONF_REPORT_UNKNOWN, default=DEFAULT_REPORT_UNKNOWN): vol.In(
            REPORT_UNKNOWN_LIST
        ),
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

    def _validate(self, value: str, type: str, errors: dict):
        if type == CONF_MAC and not validate_mac(value):
            errors[CONF_MAC] = "invalid_mac"
        elif type == CONF_UUID and not validate_uuid(value):
            errors[CONF_UUID] = "invalid_uuid"
        elif type == CONF_DEVICE_ENCRYPTION_KEY and not validate_key(value):
            errors[CONF_DEVICE_ENCRYPTION_KEY] = "invalid_key"

    def _show_main_form(self, errors=None):
        _LOGGER.error("_show_main_form: shouldn't be here")

    def _create_entry(self, uinput):
        _LOGGER.debug("_create_entry: %s", uinput)

        uinput[CONF_DEVICES] = []
        for _, dev in self._devices.items():
            if CONF_DEVICE_ENCRYPTION_KEY in dev and (
                not dev[CONF_DEVICE_ENCRYPTION_KEY] or dev[CONF_DEVICE_ENCRYPTION_KEY] == "-"
            ):
                del dev[CONF_DEVICE_ENCRYPTION_KEY]
            uinput[CONF_DEVICES].append(dev)
        return self.async_create_entry(title=DOMAIN_TITLE, data=uinput)

    @callback
    def _show_user_form(self, step_id=None, schema=None, errors=None):
        option_devices = {}
        option_devices[OPTION_LIST_DEVICE] = OPTION_LIST_DEVICE
        option_devices[OPTION_ADD_DEVICE] = OPTION_ADD_DEVICE
        for _, device in self._devices.items():
            key = dict_get_key_or(device)
            name = (
                device.get(CONF_NAME)
                if device.get(CONF_NAME)
                else device.get(key).upper()
            )
            option_devices[device.get(key).upper()] = name
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

    async def async_step_add_remove_device(self, user_input=None):
        """Add/remove device step."""
        errors = {}
        if user_input is not None:
            _LOGGER.debug("async_step_add_remove_device: %s", user_input)
            if (user_input[CONF_MAC] or user_input[CONF_UUID]) and not user_input[CONF_DEVICE_DELETE_DEVICE]:
                key = dict_get_key_or(user_input)

                if (
                    self._sel_device
                    and user_input[key].upper()
                    != self._sel_device.get(key).upper()
                ):
                    errors[key] = "cannot_change_{}".format(key)
                    user_input[key] = self._sel_device.get(key)
                else:
                    self._validate(user_input[key], key, errors)
                    self._validate(user_input[CONF_DEVICE_ENCRYPTION_KEY], CONF_DEVICE_ENCRYPTION_KEY, errors)

                if not errors:
                    # updating device configuration instead of overwriting
                    try:
                        self._devices[user_input[key].upper()].update(
                            copy.deepcopy(user_input)
                        )
                    except KeyError:
                        self._devices.update(
                            {user_input[key].upper(): copy.deepcopy(user_input)}
                        )
                    self._sel_device = {}  # prevent deletion
            if errors:
                retry_device_option_schema = vol.Schema(
                    {
                        vol.Optional(CONF_MAC, default=user_input[CONF_MAC]): str,
                        vol.Optional(CONF_UUID, default=user_input[CONF_UUID]): str,
                        vol.Optional(
                            CONF_DEVICE_ENCRYPTION_KEY,
                            default=user_input[CONF_DEVICE_ENCRYPTION_KEY],
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
                        vol.Optional(
                            CONF_DEVICE_TRACK,
                            default=user_input[CONF_DEVICE_TRACK],
                        ): cv.boolean,
                        vol.Optional(
                            CONF_DEVICE_TRACKER_SCAN_INTERVAL,
                            default=user_input[CONF_DEVICE_TRACKER_SCAN_INTERVAL],
                        ): cv.positive_int,
                        vol.Optional(
                            CONF_DEVICE_TRACKER_CONSIDER_HOME,
                            default=user_input[CONF_DEVICE_TRACKER_CONSIDER_HOME],
                        ): cv.positive_int,
                        vol.Optional(
                            CONF_DEVICE_DELETE_DEVICE,
                            default=DEFAULT_DEVICE_DELETE_DEVICE,
                        ): cv.boolean,
                    }
                )
                return self.async_show_form(
                    step_id="add_remove_device",
                    data_schema=retry_device_option_schema,
                    errors=errors,
                )
            if self._sel_device:
                # Remove device from device registry
                device_registry = await self.hass.helpers.device_registry.async_get_registry()

                conf_key = dict_get_key_or(self._sel_device)
                key = dict_get_or(self._sel_device).upper()
                device = device_registry.async_get_device({(DOMAIN, key)}, set())
                if device is None:
                    errors[conf_key] = "cannot_delete_device"
                else:
                    _LOGGER.error("Removing BLE monitor device %s from device registry", key)
                    device_registry.async_remove_device(device.id)
                _LOGGER.error("Removing BLE monitor device %s from configuration {}".format(device), key)
                del self._devices[key]
            return self._show_main_form(errors)
        device_option_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_MAC,
                    default=self._sel_device.get(
                        CONF_MAC, DEFAULT_DEVICE_MAC
                    ),
                ): str,
                vol.Optional(
                    CONF_UUID,
                    default=self._sel_device.get(
                        CONF_UUID, DEFAULT_DEVICE_UUID
                    ),
                ): str,
                vol.Optional(
                    CONF_DEVICE_ENCRYPTION_KEY,
                    default=self._sel_device.get(
                        CONF_DEVICE_ENCRYPTION_KEY, DEFAULT_DEVICE_ENCRYPTION_KEY
                    ),
                ): str,
                vol.Optional(
                    CONF_TEMPERATURE_UNIT,
                    default=self._sel_device.get(
                        CONF_TEMPERATURE_UNIT, TEMP_CELSIUS
                    ),
                ): vol.In([TEMP_CELSIUS, TEMP_FAHRENHEIT]),
                vol.Optional(
                    CONF_DEVICE_DECIMALS,
                    default=self._sel_device.get(
                        CONF_DEVICE_DECIMALS, DEFAULT_DEVICE_DECIMALS
                    ),
                ): vol.In([DEFAULT_DEVICE_DECIMALS, 0, 1, 2, 3]),
                vol.Optional(
                    CONF_DEVICE_USE_MEDIAN,
                    default=self._sel_device.get(
                        CONF_DEVICE_USE_MEDIAN, DEFAULT_DEVICE_USE_MEDIAN
                    ),
                ): vol.In([DEFAULT_DEVICE_USE_MEDIAN, True, False]),
                vol.Optional(
                    CONF_DEVICE_RESTORE_STATE,
                    default=self._sel_device.get(
                        CONF_DEVICE_RESTORE_STATE, DEFAULT_DEVICE_RESTORE_STATE
                    ),
                ): vol.In([DEFAULT_DEVICE_RESTORE_STATE, True, False]),
                vol.Optional(
                    CONF_DEVICE_RESET_TIMER,
                    default=self._sel_device.get(
                        CONF_DEVICE_RESET_TIMER, DEFAULT_DEVICE_RESET_TIMER
                    ),
                ): cv.positive_int,
                vol.Optional(
                    CONF_DEVICE_TRACK,
                    default=self._sel_device.get(
                        CONF_DEVICE_TRACK, DEFAULT_DEVICE_TRACK
                    ),
                ): cv.boolean,
                vol.Optional(
                    CONF_DEVICE_TRACKER_SCAN_INTERVAL,
                    default=self._sel_device.get(
                        CONF_DEVICE_TRACKER_SCAN_INTERVAL, DEFAULT_DEVICE_TRACKER_SCAN_INTERVAL
                    ),
                ): cv.positive_int,
                vol.Optional(
                    CONF_DEVICE_TRACKER_CONSIDER_HOME,
                    default=self._sel_device.get(
                        CONF_DEVICE_TRACKER_CONSIDER_HOME, DEFAULT_DEVICE_TRACKER_CONSIDER_HOME
                    ),
                ): cv.positive_int,
                vol.Optional(
                    CONF_DEVICE_DELETE_DEVICE,
                    default=DEFAULT_DEVICE_DELETE_DEVICE,
                ): cv.boolean,
            }
        )

        return self.async_show_form(
            step_id="add_remove_device",
            data_schema=device_option_schema,
            errors=errors,
        )


class BLEMonitorConfigFlow(BLEMonitorFlow, config_entries.ConfigFlow, domain=DOMAIN):
    """BLEMonitor config flow."""

    VERSION = 5
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
                return await self.async_step_add_remove_device()
            if user_input[CONF_DEVICES] in self._devices:
                self._sel_device = self._devices[user_input[CONF_DEVICES]]
                return await self.async_step_add_remove_device()
            if (
                "disable" in user_input[CONF_BT_INTERFACE]
                and not len(user_input[CONF_BT_INTERFACE]) == 1
            ):
                errors[CONF_BT_INTERFACE] = "cannot_disable_bt_interface"
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
                ): cv.multi_select(BT_MULTI_SELECT),
                vol.Optional(
                    CONF_BT_AUTO_RESTART,
                    default=self.config_entry.options.get(
                        CONF_BT_AUTO_RESTART, DEFAULT_BT_AUTO_RESTART
                    ),
                ): cv.boolean,
                vol.Optional(
                    CONF_ACTIVE_SCAN,
                    default=self.config_entry.options.get(
                        CONF_ACTIVE_SCAN, DEFAULT_ACTIVE_SCAN
                    ),
                ): cv.boolean,
                vol.Optional(
                    CONF_DISCOVERY,
                    default=self.config_entry.options.get(
                        CONF_DISCOVERY, DEFAULT_DISCOVERY
                    ),
                ): cv.boolean,
                vol.Optional(
                    CONF_PERIOD,
                    default=self.config_entry.options.get(
                        CONF_PERIOD, DEFAULT_PERIOD
                    ),
                ): cv.positive_int,
                vol.Optional(
                    CONF_USE_MEDIAN,
                    default=self.config_entry.options.get(
                        CONF_USE_MEDIAN, DEFAULT_USE_MEDIAN
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
                    CONF_RESTORE_STATE,
                    default=self.config_entry.options.get(
                        CONF_RESTORE_STATE, DEFAULT_RESTORE_STATE
                    ),
                ): cv.boolean,
                vol.Optional(
                    CONF_REPORT_UNKNOWN,
                    default=self.config_entry.options.get(
                        CONF_REPORT_UNKNOWN, DEFAULT_REPORT_UNKNOWN
                    ),
                ): vol.In(REPORT_UNKNOWN_LIST),
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
                CONFIG_IS_FLOW in self.config_entry.options
                and not self.config_entry.options[CONFIG_IS_FLOW]
            ):
                return self.async_abort(reason="not_in_use")
            if user_input[CONF_DEVICES] == OPTION_ADD_DEVICE:
                self._sel_device = {}
                return await self.async_step_add_remove_device()
            if user_input[CONF_DEVICES] in self._devices:
                self._sel_device = self._devices[user_input[CONF_DEVICES]]
                return await self.async_step_add_remove_device()
            if "disable" in user_input[CONF_BT_INTERFACE] and not len(user_input[CONF_BT_INTERFACE]) == 1:
                errors[CONF_BT_INTERFACE] = "cannot_disable_bt_interface"
            return self._create_entry(user_input)
        _LOGGER.debug("async_step_init (before): %s", self.config_entry.options)

        if (
            CONFIG_IS_FLOW in self.config_entry.options
            and not self.config_entry.options[CONFIG_IS_FLOW]
        ):
            options_schema = vol.Schema({vol.Optional("not_in_use", default=""): str})
            return self.async_show_form(
                step_id="init", data_schema=options_schema, errors=errors or {}
            )
        for dev in self.config_entry.options.get(CONF_DEVICES):
            self._devices[dict_get_or(dev).upper()] = dev
        devreg = await self.hass.helpers.device_registry.async_get_registry()
        for dev in device_registry.async_entries_for_config_entry(
            devreg, self.config_entry.entry_id
        ):
            for iddomain, id in dev.identifiers:
                if iddomain != DOMAIN:
                    continue
                name = dev.name_by_user if dev.name_by_user else dev.name
                if id in self._devices:
                    self._devices[id][CONF_NAME] = name
                else:
                    self._devices[id] = {
                        detect_conf_type(id): id, CONF_NAME: name
                    }

        # sort devices by name
        sorteddev_tuples = sorted(
            self._devices.items(), key=lambda item: item[1].get(
                "name", dict_get_or(item[1])
            )
        )
        self._devices = dict(sorteddev_tuples)
        self.hass.config_entries.async_update_entry(
            self.config_entry, unique_id=self.config_entry.entry_id
        )
        return self._show_main_form(errors)
