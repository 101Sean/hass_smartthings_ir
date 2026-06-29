import logging
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode, ClimateEntityFeature
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, CONF_DEVICE_ID, CONF_NAME
from .api import SmartThingsIRAPI

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    if data.get("device_type") == "ac":
        async_add_entities([SmartThingsIRClimate(hass, data[CONF_DEVICE_ID], data[CONF_NAME])])

class SmartThingsIRClimate(ClimateEntity):
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = 18
    _attr_max_temp = 30
    _attr_target_temperature_step = 1
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.DRY, HVACMode.AUTO]
    _attr_fan_modes = ["low", "medium", "high"]

    def __init__(self, hass, device_id, name):
        self.hass = hass
        self._device_id = device_id
        self._attr_name = name
        self._attr_unique_id = f"smartthings_ir_climate_{device_id}"
        self._attr_target_temperature = 24
        self._attr_hvac_mode = HVACMode.OFF
        self._attr_fan_mode = "medium"
        self._api = SmartThingsIRAPI(hass)

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        if hvac_mode == HVACMode.OFF:
            await self._send_command("switch", "off")
        else:
            await self._send_command("switch", "on")
            mode_map = {
                HVACMode.COOL: "cool",
                HVACMode.DRY: "dry",
                HVACMode.AUTO: "auto"
            }
            await self._send_command("AIR_CONDITIONER_MODE", "SET_AIR_CONDITIONER_MODE", [mode_map.get(hvac_mode, "cool")])
        self._attr_hvac_mode = hvac_mode
        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs) -> None:
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is not None:
            self._attr_target_temperature = temp
            await self._send_command("THERMOSTAT_COOLING_SETPOINT", "SET_COOLING_SETPOINT", [temp])
            self.async_write_ha_state()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        self._attr_fan_mode = fan_mode
        await self._send_command("AIR_CONDITIONER_FAN_MODE", "SET_FAN_MODE", [fan_mode])
        self.async_write_ha_state()

    async def _send_command(self, capability, command, arguments=None):
        await self._api.command(
            ha_device_id=self._device_id,
            capability=capability,
            command=command,
            arguments=arguments or [],
        )