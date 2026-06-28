import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_DEVICE_ID, CONF_DEVICE_TYPE, CONF_NAME, DEVICE_TYPES

class SmartThingsIRConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID]
            device_type = user_input[CONF_DEVICE_TYPE]
            name = user_input[CONF_NAME]
            await self.async_set_unique_id(device_id)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=name,
                data={
                    CONF_DEVICE_ID: device_id,
                    CONF_DEVICE_TYPE: device_type,
                    CONF_NAME: name,
                }
            )
        data_schema = vol.Schema({
            vol.Required(CONF_NAME, default="SmartThings IR Device"): str,
            vol.Required(CONF_DEVICE_ID): str,
            vol.Required(CONF_DEVICE_TYPE, default="tv"): vol.In(DEVICE_TYPES),
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(step_id="init")