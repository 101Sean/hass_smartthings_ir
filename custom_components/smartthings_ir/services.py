import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from .const import DOMAIN
from .api import SmartThingsIRAPI

_LOGGER = logging.getLogger(__name__)


async def async_register_services(hass: HomeAssistant) -> None:
    
    async def handle_show_device_id(call: ServiceCall) -> None:
        ha_device_id = call.data.get("device_id")
        
        if not ha_device_id:
            raise HomeAssistantError("device_id is required")
        
        api = SmartThingsIRAPI(hass)
        st_device_id, st_entry_id = await api._resolve_st_ids(ha_device_id)
        
        _LOGGER.debug("UUID shown for device: %s -> %s", ha_device_id, st_device_id)
    
    hass.services.async_register(DOMAIN, "show_device_id", handle_show_device_id)
    _LOGGER.debug("Services registered for %s", DOMAIN)


async def async_unregister_services(hass: HomeAssistant) -> None:
    hass.services.async_remove(DOMAIN, "show_device_id")
    _LOGGER.debug("Services unregistered for %s", DOMAIN)