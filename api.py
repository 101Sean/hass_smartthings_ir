import logging
import aiohttp
from typing import Optional, Tuple

from homeassistant.components.smartthings.const import DOMAIN as ST_DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.exceptions import HomeAssistantError

from pysmartthings import Capability, Command

_LOGGER = logging.getLogger(__name__)


class SmartThingsIRAPI:
    def __init__(self, hass: HomeAssistant):
        self.hass = hass

    async def _resolve_st_ids(self, ha_device_id: str) -> Tuple[str, str]:
        dev_reg = dr.async_get(self.hass)
        device_entry = dev_reg.async_get(ha_device_id)
        if not device_entry:
            raise HomeAssistantError(f"No HA device found: {ha_device_id}")

        st_device_id: Optional[str] = None
        for domain, ident in device_entry.identifiers:
            if domain == ST_DOMAIN:
                st_device_id = ident
                break
        if not st_device_id:
            raise HomeAssistantError("Device is not linked to SmartThings.")

        st_entry_id: Optional[str] = None
        for entry_id in device_entry.config_entries:
            entry = self.hass.config_entries.async_get_entry(entry_id)
            if entry and entry.domain == ST_DOMAIN and entry.state == ConfigEntryState.LOADED:
                st_entry_id = entry.entry_id
                break
        if not st_entry_id:
            raise HomeAssistantError("No loaded SmartThings config entry for this device.")

        return st_device_id, st_entry_id

    async def _get_client(self, st_entry_id: str):
        entry = self.hass.config_entries.async_get_entry(st_entry_id)
        if not entry or not entry.runtime_data:
            raise HomeAssistantError("SmartThings entry not available or not loaded.")
        return entry.runtime_data.client

    async def command(
        self,
        ha_device_id: str,
        capability: str,
        command: str,
        arguments: Optional[list] = None,
        component: str = "main",
    ) -> bool:
        try:
            st_device_id, st_entry_id = await self._resolve_st_ids(ha_device_id)

            client = await self._get_client(st_entry_id)

            special_caps = {
                "STATELESS_AUDIO_VOLUME_BUTTON": "statelessAudioVolumeButton",
                "STATELESS_CHANNEL_BUTTON": "statelessChannelButton",
                "STATELESS_AUDIO_MUTE_BUTTON": "statelessAudioMuteButton",
                "STATELESS_POWER_TOGGLE_BUTTON": "statelessPowerToggleButton",
            }

            upper_input = capability.upper()
            if upper_input in special_caps:
                mapped_capability = special_caps[upper_input]
            else:
                mapped_capability = getattr(Capability, upper_input, capability)

            mapped_command = getattr(Command, command.upper(), command)

            _LOGGER.debug(
                "Command -> device=%s, capability=%s, command=%s, args=%s",
                st_device_id, mapped_capability, mapped_command, arguments
            )

            await client.execute_device_command(
                device_id=st_device_id,
                capability=mapped_capability,
                command=mapped_command,
                component=component,
                argument=arguments or [],
            )

            return True

        except Exception as e:
            _LOGGER.error("Command failed: %s", e)
            return False