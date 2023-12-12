from bleak import BleakClient
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.components import bluetooth
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, SERVICE
from .utils import (
    notification_handler,
    getNotifyCharacteristic,
    sendCommand,
    getLightStateCommand,
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the Lights App component from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    address = entry.data.get(CONF_ADDRESS)

    ble_device = bluetooth.async_ble_device_from_address(
        hass, address, connectable=True
    )
    if ble_device:
        hass.data[DOMAIN][entry.entry_id] = {}
        hass.data[DOMAIN][entry.entry_id]["connection"] = {
            "client": BleakClient(ble_device)
        }
        client = hass.data[DOMAIN][entry.entry_id]["connection"]["client"]
        await client.connect()
        hass.data[DOMAIN][entry.entry_id]["connection"][
            "service"
        ] = client.services.get_service(SERVICE)
        communicationService = hass.data[DOMAIN][entry.entry_id]["connection"][
            "service"
        ]
        if communicationService:
            await client.start_notify(
                getNotifyCharacteristic(communicationService), notification_handler
            )

            await sendCommand(
                client,
                communicationService,
                getLightStateCommand(),
            )

            hass.async_create_task(
                hass.config_entries.async_forward_entry_setup(entry, "light")
            )
        return True
    raise ConfigEntryNotReady()
