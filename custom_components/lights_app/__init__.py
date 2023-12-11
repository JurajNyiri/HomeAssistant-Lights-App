import datetime
import hashlib
import logging
import asyncio
from bleak import BleakScanner,BleakClient,BleakGATTCharacteristic
from led_ble import BLEAK_EXCEPTIONS, LEDBLE

from homeassistant.core import HomeAssistant, callback
from homeassistant.components.bluetooth.match import ADDRESS, BluetoothCallbackMatcher
from homeassistant.components.ffmpeg import CONF_EXTRA_ARGUMENTS
from homeassistant.config_entries import ConfigEntry
from homeassistant.components import bluetooth
from homeassistant.const import (
    CONF_IP_ADDRESS,
    CONF_USERNAME,
    CONF_PASSWORD,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.exceptions import (
    ConfigEntryNotReady,
    ConfigEntryAuthFailed,
    DependencyError,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt
from homeassistant.components.media_source.error import Unresolvable
import homeassistant.helpers.entity_registry
from homeassistant.const import CONF_ADDRESS

from .const import DOMAIN, SERVICE, NOTIFY_CHARACTERISTIC, LOGGER
import logging
from typing import TYPE_CHECKING

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth.active_update_coordinator import (
    ActiveBluetoothDataUpdateCoordinator,
)
from homeassistant.core import CoreState, HomeAssistant, callback

from bleak.backends.device import BLEDevice


_LOGGER = logging.getLogger(__name__)
TURN_OFF = "01 01 01 00"
TURN_ON = "01 01 01 01"
BRIGTNESS_10 = "03 01 01 0a"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.warn("async_setup_entry")
    """Set up the Lights App component from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    address = entry.data.get(CONF_ADDRESS)

    def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
        print("notification_handler")
        print(data)
        LOGGER.warn("notification_handler")
        LOGGER.warn(data)

    ble_device = bluetooth.async_ble_device_from_address(hass, address, connectable=True)
    if ble_device:
        hass.data[DOMAIN][entry.entry_id] = {}
        hass.data[DOMAIN][entry.entry_id]["connection"] = {
            "client": BleakClient(ble_device)
        }
        client = hass.data[DOMAIN][entry.entry_id]["connection"]['client']
        await client.connect()
        hass.data[DOMAIN][entry.entry_id]["connection"]['service'] = client.services.get_service(SERVICE)
        communicationService = hass.data[DOMAIN][entry.entry_id]["connection"]['service']
        if communicationService:
            writeCharacteristic = communicationService.characteristics[0]
            notifyCharacteristic = communicationService.get_characteristic(NOTIFY_CHARACTERISTIC)
            LOGGER.warn(notifyCharacteristic)
            await client.start_notify(notifyCharacteristic, notification_handler)
            command = bytearray.fromhex(TURN_OFF.replace(" ", ""))
            await client.write_gatt_char(writeCharacteristic, command, True)
            
            hass.async_create_task(
                hass.config_entries.async_forward_entry_setup(entry, "light")
            )
        return True
    raise ConfigEntryNotReady()

