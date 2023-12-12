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
    LOGGER.debug("setupConnection")
    if not hass.data[DOMAIN][config_entry.entry_id]["connection"]["connecting"]:
        LOGGER.debug("Initiating connection attempt...")
        try:
            hass.data[DOMAIN][config_entry.entry_id]["connection"]["connecting"] = True
            ble_device = bluetooth.async_ble_device_from_address(
                hass, address, connectable=True
            )
            if ble_device:
                LOGGER.debug("BLE Device found, connecting...")
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
                LOGGER.debug(
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
                        hass.data[DOMAIN][config_entry.entry_id],
                        client,
                        communicationService,
                        getLightStateCommand(),
                    )
                    await sendCommand(
                        hass.data[DOMAIN][config_entry.entry_id],
                        client,
                        communicationService,
                        getModeStateCommand(),
                    )

                LOGGER.debug("Connection completed.")
            else:
                LOGGER.debug("BLE Device not found.")
        except Exception as err:
            LOGGER.error(err)
        hass.data[DOMAIN][config_entry.entry_id]["connection"]["connecting"] = False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_forward_entry_unload(entry, "switch")
    await hass.config_entries.async_forward_entry_unload(entry, "light")
    await hass.config_entries.async_forward_entry_unload(entry, "number")
    if hass.data[DOMAIN][entry.entry_id]["connection"]["connected"]:
        client = hass.data[DOMAIN][entry.entry_id]["connection"]["client"]
        await client.disconnect()

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the Lights App component from a config entry."""
    LOGGER.debug("async_setup_entry")
    hass.data.setdefault(DOMAIN, {})

    address = entry.data.get(CONF_ADDRESS)

    hass.data[DOMAIN][entry.entry_id] = {
        "address": address,
        "entities": [],
        "state": None,
        "statePending": True,
        "mode": None,
        "modePending": True,
        "brightness": None,
        "brightnessPending": True,
        "connection": {"connected": False, "connecting": False},
    }

    await setupConnection(hass, address, entry)

    if hass.data[DOMAIN][entry.entry_id]["connection"]["connected"]:

        async def async_update_data():
            LOGGER.debug("async_update_data - entry")

            if not hass.data[DOMAIN][entry.entry_id]["connection"]["connected"]:
                LOGGER.debug("Not connected, reloading...")
                await hass.config_entries.async_reload(entry.entry_id)
            else:
                await sendCommand(
                    hass.data[DOMAIN][entry.entry_id],
                    hass.data[DOMAIN][entry.entry_id]["connection"]["client"],
                    hass.data[DOMAIN][entry.entry_id]["connection"]["service"],
                    getLightStateCommand(),
                )
                await sendCommand(
                    hass.data[DOMAIN][entry.entry_id],
                    hass.data[DOMAIN][entry.entry_id]["connection"]["client"],
                    hass.data[DOMAIN][entry.entry_id]["connection"]["service"],
                    getModeStateCommand(),
                )

        lightsAppCoordinator = DataUpdateCoordinator(
            hass,
            LOGGER,
            name="Lights App resource status",
            update_method=async_update_data,
        )
        hass.data[DOMAIN][entry.entry_id]["coordinator"] = lightsAppCoordinator

        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, "light")
        )
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, "switch")
        )
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, "number")
        )
        return True
    raise ConfigEntryNotReady()
