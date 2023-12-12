from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

from .entities import LightsAppNumberEntity
from .const import LOGGER
from .utils import sendCommand, getBrightnessCommand


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    LOGGER.debug("Setting up number")
    lightsAppBrightness = LightsAppBrightness(
        hass, config_entry, hass.data[DOMAIN][config_entry.entry_id]
    )
    hass.data[DOMAIN][config_entry.entry_id]["entities"].append(lightsAppBrightness)
    async_add_entities([lightsAppBrightness])


class LightsAppBrightness(LightsAppNumberEntity):
    def __init__(self, hass: HomeAssistant, config_entry, entryData):
        self._attr_native_min_value = 10
        self._attr_native_max_value = 99
        LightsAppNumberEntity.__init__(
            self, hass, config_entry, entryData, "Brightness"
        )
        self.setState()

    def setState(self):
        if "brightness" in self._entryData:
            if self._entryData["brightness"] is None:
                self._attr_state = STATE_UNAVAILABLE
            else:
                self._attr_state = self._entryData["brightness"]

    async def async_update(self) -> None:
        if not self._entryData["brightnessPending"]:
            self.setState()
        await self._entryData["coordinator"].async_request_refresh()

    async def async_set_native_value(self, value: float) -> None:
        command = getBrightnessCommand(int(value))
        LOGGER.debug("Setting to:")
        LOGGER.debug(int(value))
        LOGGER.debug(command)
        await sendCommand(self._client, self._service, getBrightnessCommand(int(value)))

    @property
    def state(self):
        return self._attr_state
