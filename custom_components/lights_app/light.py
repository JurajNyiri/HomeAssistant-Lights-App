from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode

from .const import DOMAIN

from .entities import LightsAppLightEntity
from .const import LOGGER
from .utils import (
    convert_device_brightness_to_ha,
    convert_ha_brightness_to_device,
    getBrightnessCommand,
    getTurnOnCommand,
    getTurnOffCommand,
    sendCommand,
)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    LOGGER.debug("Setting up lights")
    on_off = LightsAppTurnOnOff(
        hass, config_entry, hass.data[DOMAIN][config_entry.entry_id]
    )
    hass.data[DOMAIN][config_entry.entry_id]["entities"].append(on_off)
    async_add_entities([on_off])


class LightsAppTurnOnOff(LightsAppLightEntity):
    def __init__(self, hass: HomeAssistant, config_entry, entryData):
        LightsAppLightEntity.__init__(self, hass, config_entry, entryData, "Light")

    async def async_update(self) -> None:
        await self._entryData["coordinator"].async_request_refresh()

    async def async_turn_on(self, **kwargs) -> None:
        if ATTR_BRIGHTNESS in kwargs:
            device_brightness = convert_ha_brightness_to_device(kwargs[ATTR_BRIGHTNESS])
            await sendCommand(
                self._entryData,
                self._client,
                self._service,
                getBrightnessCommand(device_brightness),
            )

        await sendCommand(
            self._entryData, self._client, self._service, getTurnOnCommand()
        )

    async def async_turn_off(self) -> None:
        await sendCommand(
            self._entryData, self._client, self._service, getTurnOffCommand()
        )

    @property
    def available(self):
        return (self._entryData.get("state", None) is not None
            and self._entryData.get("brightness", None) is not None)

    @property
    def is_on(self):
        return self._entryData["state"]

    @property
    def brightness(self):
        return convert_device_brightness_to_ha(self._entryData["brightness"])

    @property
    def supported_color_modes(self):
        return {ColorMode.BRIGHTNESS}

    @property
    def color_mode(self):
        return ColorMode.BRIGHTNESS
