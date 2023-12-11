from homeassistant.core import HomeAssistant
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_ADDRESS

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components import bluetooth
from bleak import BleakScanner,BleakClient

from .const import DOMAIN, LOGGER, SERVICE

TURN_ON = "01 01 01 01"

TURN_OFF = "01 01 01 00"

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    LOGGER.warn("Setting up switches")

    on_off = LightsAppTurnOnOff(hass, config_entry)
    async_add_entities([on_off])


class LightsAppTurnOnOff(SwitchEntity):
    def __init__(self, hass: HomeAssistant, config_entry):
        self._attr_is_on = False
        self._hass = hass
        self._client = hass.data[DOMAIN][config_entry.entry_id]["connection"]['client']
        self._service = hass.data[DOMAIN][config_entry.entry_id]["connection"]['service']
        self._entry = config_entry
        self._enabled = False
        self._is_cam_entity = False
        self._is_noise_sensor = False
        self._name = "lightsapp"
        self._name_suffix = "lightsapp"
        SwitchEntity.__init__(self)

    async def async_update(self) -> None:
        LOGGER.warn("Debug3")

    async def async_turn_on(self) -> None:
        writeCharacteristic = self._service.characteristics[0]
        command = bytearray.fromhex(TURN_ON.replace(" ", ""))
        await self._client.write_gatt_char(writeCharacteristic, command, True)

    async def async_turn_off(self) -> None:
        writeCharacteristic = self._service.characteristics[0]
        command = bytearray.fromhex(TURN_OFF.replace(" ", ""))
        await self._client.write_gatt_char(writeCharacteristic, command, True)
