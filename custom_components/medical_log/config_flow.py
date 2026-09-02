from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import (
    CONF_CHILD_NAME,
    CONF_MEDICATION_1,
    CONF_MEDICATION_2,
    DEFAULT_MEDICATION_1,
    DEFAULT_MEDICATION_2,
    DOMAIN,
)


class MedicalLogConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            child_name = user_input[CONF_CHILD_NAME].strip()
            await self.async_set_unique_id(child_name.casefold())
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=child_name, data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_CHILD_NAME): str,
                vol.Required(CONF_MEDICATION_1, default=DEFAULT_MEDICATION_1): str,
                vol.Required(CONF_MEDICATION_2, default=DEFAULT_MEDICATION_2): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)
