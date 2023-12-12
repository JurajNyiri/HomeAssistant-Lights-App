from bleak import BleakClient
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.components import bluetooth
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, SERVICE, LOGGER
from .utils import (
    notification_handler,
    getNotifyCharacteristic,
    sendCommand,
    getLightStateCommand,
    disconnect_handler,
)

from led_ble import LEDBLE

from bleak_retry_connector import establish_connection, BleakClientWithServiceCache


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the Lights App component from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    address = entry.data.get(CONF_ADDRESS)

    ble_device = bluetooth.async_ble_device_from_address(
        hass, address, connectable=True
    )
    if ble_device:
        hass.data[DOMAIN][entry.entry_id] = {
            "address": address,
            "entities": [],
            "state": None,
            "statePending": True,
            "connection": {},
        }

        # todo what happens if connection fails?
        hass.data[DOMAIN][entry.entry_id]["connection"][
            "client"
        ] = await establish_connection(
            BleakClientWithServiceCache,
            ble_device,
            address,
            disconnect_handler(hass.data[DOMAIN][entry.entry_id]),
            use_services_cache=True,
        )
        hass.data[DOMAIN][entry.entry_id]["connection"]["connected"] = True
        # todo add refresh that detects whether we are connected or not

        client = hass.data[DOMAIN][entry.entry_id]["connection"]["client"]
        hass.data[DOMAIN][entry.entry_id]["connection"][
            "service"
        ] = client.services.get_service(SERVICE)
        communicationService = hass.data[DOMAIN][entry.entry_id]["connection"][
            "service"
        ]
        if communicationService:
            await client.start_notify(
                getNotifyCharacteristic(communicationService),
                notification_handler(hass.data[DOMAIN][entry.entry_id]),
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
