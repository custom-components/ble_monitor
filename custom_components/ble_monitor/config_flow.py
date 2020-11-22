"""Config flow for BLE Monitor."""
import logging

from homeassistant import config_entries
from .const import (
    DOMAIN
)

_LOGGER = logging.getLogger(__name__)

class BLEMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            title = f"BLE Monitor"
            await self.async_set_unique_id(title)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=title, data=user_input)

        return self._show_user_form(errors)

    async def async_step_import(self, user_input=None):
        """Handle import."""
        return self.async_step_user(user_input)

