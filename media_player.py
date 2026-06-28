import logging
from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import MediaPlayerEntityFeature, MediaPlayerState
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
    device_type = data.get("device_type")
    if device_type in ("tv", "settop"):
        async_add_entities([SmartThingsIRMediaPlayer(hass, data[CONF_DEVICE_ID], data[CONF_NAME], device_type)])

class SmartThingsIRMediaPlayer(MediaPlayerEntity):
    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_OFF |
        MediaPlayerEntityFeature.VOLUME_STEP |
        MediaPlayerEntityFeature.VOLUME_MUTE |
        MediaPlayerEntityFeature.NEXT_TRACK |
        MediaPlayerEntityFeature.PREVIOUS_TRACK
    )
    _attr_assumed_state = True

    def __init__(self, hass, device_id, name, device_type):
        self.hass = hass
        self._device_id = device_id
        self._attr_name = name
        self._attr_device_class = "tv"
        self._attr_unique_id = f"smartthings_ir_media_player_{device_id}"
        self._attr_state = MediaPlayerState.ON
        self._device_type = device_type
        self._api = SmartThingsIRAPI(hass)

    async def async_turn_on(self):
        await self._send_command("STATELESS_POWER_TOGGLE_BUTTON", "SET_BUTTON", ["powerToggle"])
        self._attr_state = MediaPlayerState.ON
        self.async_write_ha_state()

    async def async_turn_off(self):
        await self._send_command("STATELESS_POWER_TOGGLE_BUTTON", "SET_BUTTON", ["powerToggle"])
        self._attr_state = MediaPlayerState.ON
        self.async_write_ha_state()

    async def async_volume_up(self):
        await self._send_command("STATELESS_AUDIO_VOLUME_BUTTON", "SET_BUTTON", ["volumeUp"])

    async def async_volume_down(self):
        await self._send_command("STATELESS_AUDIO_VOLUME_BUTTON", "SET_BUTTON", ["volumeDown"])

    async def async_mute_volume(self, mute):
        await self._send_command("STATELESS_AUDIO_MUTE_BUTTON", "SET_BUTTON", ["muteToggle"])

    async def async_media_next_track(self):
        await self._send_command("STATELESS_CHANNEL_BUTTON", "SET_BUTTON", ["channelUp"])

    async def async_media_previous_track(self):
        await self._send_command("STATELESS_CHANNEL_BUTTON", "SET_BUTTON", ["channelDown"])

    async def async_media_play(self):
        pass

    async def async_media_pause(self):
        pass

    async def _send_command(self, capability, command, arguments=None):
        await self._api.command(
            ha_device_id=self._device_id,
            capability=capability,
            command=command,
            arguments=arguments or [],
        )