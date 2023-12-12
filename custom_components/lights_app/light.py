import asyncio
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

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
    LOGGER.debug("Setting up lights")
    on_off = LightsAppTurnOnOff(
        hass, config_entry, hass.data[DOMAIN][config_entry.entry_id]
    )
    hass.data[DOMAIN][config_entry.entry_id]["entities"].append(on_off)
    async_add_entities([on_off])


class LightsAppTurnOnOff(LightsAppLightEntity):
    def __init__(self, hass: HomeAssistant, config_entry, entryData):
        LightsAppLightEntity.__init__(self, hass, config_entry, entryData, "Light")
        self.setState()

    def setState(self):
        if "state" in self._entryData:
            if self._entryData["state"] is None:
                self._attr_state = STATE_UNAVAILABLE
            else:
                self._attr_state = "on" if self._entryData["state"] else "off"

    async def async_update(self) -> None:
        if not self._entryData["statePending"]:
            self.setState()
        await self._entryData["coordinator"].async_request_refresh()

    async def async_turn_on(self) -> None:
        await sendCommand(
            self._entryData, self._client, self._service, getTurnOnCommand()
        )

    async def async_turn_off(self) -> None:
        await sendCommand(
            self._entryData, self._client, self._service, getTurnOffCommand()
        )

    @property
    def state(self):
        return self._attr_state
