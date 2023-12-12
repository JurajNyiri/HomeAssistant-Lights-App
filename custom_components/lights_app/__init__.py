from bleak_retry_connector import establish_connection, BleakClientWithServiceCache
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.components import bluetooth
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, SERVICE, LOGGER
from .utils import (
    notification_handler,
    getNotifyCharacteristic,
    sendCommand,
    getLightStateCommand,
    disconnect_handler,
    getModeStateCommand,
)


async def setupConnection(hass, address, config_entry):
    LOGGER.warn("setupConnection")
    if not hass.data[DOMAIN][config_entry.entry_id]["connection"]["connecting"]:
        LOGGER.warn("Initiating connection attempt...")
        try:
            hass.data[DOMAIN][config_entry.entry_id]["connection"]["connecting"] = True
            ble_device = bluetooth.async_ble_device_from_address(
                hass, address, connectable=True
            )
            if ble_device:
                LOGGER.warn("BLE Device found, connecting...")
                hass.data[DOMAIN][config_entry.entry_id]["connection"][
                    "client"
                ] = await establish_connection(
                    BleakClientWithServiceCache,
                    ble_device,
                    name=address,
                    disconnected_callback=disconnect_handler(
                        hass.data[DOMAIN][config_entry.entry_id]
                    ),
                    use_services_cache=True,
                    max_attempts=1,
                )
                hass.data[DOMAIN][config_entry.entry_id]["connection"][
                    "connected"
                ] = True
                LOGGER.warn(
                    "Connected successfully, setting up subscribers and getting data..."
                )
                client = hass.data[DOMAIN][config_entry.entry_id]["connection"][
                    "client"
                ]
                hass.data[DOMAIN][config_entry.entry_id]["connection"][
                    "service"
                ] = client.services.get_service(SERVICE)
                communicationService = hass.data[DOMAIN][config_entry.entry_id][
                    "connection"
                ]["service"]

                if communicationService:
                    await client.start_notify(
                        getNotifyCharacteristic(communicationService),
                        notification_handler(hass.data[DOMAIN][config_entry.entry_id]),
                    )

                    await sendCommand(
                        client,
                        communicationService,
                        getLightStateCommand(),
                    )
                    await sendCommand(
                        client,
                        communicationService,
                        getModeStateCommand(),
                    )

                LOGGER.warn("Connection completed.")
            else:
                LOGGER.warn("BLE Device not found.")
        except Exception as err:
            LOGGER.error(err)
        hass.data[DOMAIN][config_entry.entry_id]["connection"]["connecting"] = False


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
            "mode": None,
            "modePending": True,
            "connection": {"connected": False, "connecting": False},
        }

        async def async_update_data():
            LOGGER.warn("async_update_data - entry")
            if not hass.data[DOMAIN][entry.entry_id]["connection"]["connected"]:
                LOGGER.warn("Not connected, reconnecting...")
                await setupConnection(hass, address, entry)

        lightsAppCoordinator = DataUpdateCoordinator(
            hass,
            LOGGER,
            name="Lights App resource status",
            update_method=async_update_data,
        )
        hass.data[DOMAIN][entry.entry_id]["coordinator"] = lightsAppCoordinator

        await setupConnection(hass, address, entry)

        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, "light")
        )
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, "switch")
        )

        return True
    raise ConfigEntryNotReady()
