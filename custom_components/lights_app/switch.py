from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

from .entities import LightsAppSwitchEntity
from .const import LOGGER
from .utils import sendCommand, getModeCommand


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    LOGGER.warn("Setting up switches")
    modeSwitches = [
        LightsAppModeSwitch(
            hass,
            config_entry,
            hass.data[DOMAIN][config_entry.entry_id],
            "Stay on",
            "stay_on",
        ),
        LightsAppModeSwitch(
            hass,
            config_entry,
            hass.data[DOMAIN][config_entry.entry_id],
            "Fast twinkling",
            "fast_twinkling",
        ),
        LightsAppModeSwitch(
            hass,
            config_entry,
            hass.data[DOMAIN][config_entry.entry_id],
            "Fade away",
            "fade_away",
        ),
        LightsAppModeSwitch(
            hass,
            config_entry,
            hass.data[DOMAIN][config_entry.entry_id],
            "Twinkling in phase",
            "twinkling_in_phase",
        ),
        LightsAppModeSwitch(
            hass,
            config_entry,
            hass.data[DOMAIN][config_entry.entry_id],
            "Fade away in phase",
            "fade_away_in_phase",
        ),
        LightsAppModeSwitch(
            hass,
            config_entry,
            hass.data[DOMAIN][config_entry.entry_id],
            "Phasing",
            "phasing",
        ),
        LightsAppModeSwitch(
            hass, config_entry, hass.data[DOMAIN][config_entry.entry_id], "Wave", "wave"
        ),
    ]
    for mode in modeSwitches:
        hass.data[DOMAIN][config_entry.entry_id]["entities"].append(mode)
    async_add_entities(modeSwitches)


class LightsAppModeSwitch(LightsAppSwitchEntity):
    def __init__(self, hass: HomeAssistant, config_entry, entryData, name, mode):
        self._mode = mode
        LightsAppSwitchEntity.__init__(self, hass, config_entry, entryData, name)
        self.setState()

    def setState(self):
        if "mode" in self._entryData:
            if self._entryData["mode"] is None:
                self._attr_state = STATE_UNAVAILABLE
            else:
                self._attr_state = (
                    "on" if self._entryData["mode"][self._mode] else "off"
                )

    async def async_update(self) -> None:
        if not self._entryData["modePending"]:
            self.setState()
        await self._entryData["coordinator"].async_request_refresh()

    async def async_turn_on(self) -> None:
        self._entryData["mode"][self._mode] = True
        await sendCommand(
            self._client, self._service, getModeCommand(self._entryData["mode"])
        )

    async def async_turn_off(self) -> None:
        self._entryData["mode"][self._mode] = False
        await sendCommand(
            self._client, self._service, getModeCommand(self._entryData["mode"])
        )

    @property
    def state(self):
        return self._attr_state
