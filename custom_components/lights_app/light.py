from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entities import LightsAppLightEntity
from .const import LOGGER
from .utils import getTurnOnCommand, getTurnOffCommand, sendCommand


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    LOGGER.warn("Setting up lights")

    on_off = LightsAppTurnOnOff(hass, config_entry)
    async_add_entities([on_off])


class LightsAppTurnOnOff(LightsAppLightEntity):
    def __init__(self, hass: HomeAssistant, config_entry):
        LightsAppLightEntity.__init__(self, hass, config_entry, "Light")

    async def async_update(self) -> None:
        LOGGER.warn("Debug3")

    async def async_turn_on(self) -> None:
        await sendCommand(self._client, self._service, getTurnOnCommand())

    async def async_turn_off(self) -> None:
        await sendCommand(self._client, self._service, getTurnOffCommand())
