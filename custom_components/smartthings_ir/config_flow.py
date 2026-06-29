import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.components.smartthings.const import DOMAIN as ST_DOMAIN
from homeassistant.config_entries import ConfigEntryState
from .const import DOMAIN, CONF_DEVICE_ID, CONF_DEVICE_TYPE, CONF_NAME, DEVICE_TYPES

_LOGGER = logging.getLogger(__name__)

class SmartThingsIRConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._devices = {}
        self._selected_device = None

    async def async_step_user(self, user_input=None):
        errors = {}

        st_entry = None
        for entry in self.hass.config_entries.async_entries():
            if entry.domain == ST_DOMAIN and entry.state == ConfigEntryState.LOADED:
                st_entry = entry
                break

        if not st_entry:
            return self.async_abort(reason="no_smartthings_integration")

        if not self._devices:
            try:
                client = st_entry.runtime_data.client
                devices = await client.devices()
                self._devices = {
                    device.device_id: f"{device.name} ({device.device_id})"
                    for device in devices
                    if any("stateless" in cap for cap in device.capabilities)
                }
            except Exception as e:
                _LOGGER.error("Failed to fetch SmartThings devices: %s", e)
                return self.async_abort(reason="cannot_connect")

        if not self._devices:
            return self.async_abort(reason="no_ir_devices")

        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID]
            device_type = user_input[CONF_DEVICE_TYPE]
            name = user_input[CONF_NAME]

            if not name or name == "SmartThings IR Device":
                for dev_id, dev_name in self._devices.items():
                    if dev_id == device_id:
                        clean_name = dev_name.split(" (")[0]
                        name = clean_name
                        break

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

        device_options = {device_id: display_name for device_id, display_name in self._devices.items()}
        data_schema = vol.Schema({
            vol.Required(CONF_NAME, default="SmartThings IR Device"): str,
            vol.Required(CONF_DEVICE_ID): vol.In(device_options),
            vol.Required(CONF_DEVICE_TYPE, default="tv"): vol.In(DEVICE_TYPES),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "integration_name": "SmartThings IR Controller"
            }
        )

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