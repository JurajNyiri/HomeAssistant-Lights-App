from bleak import BleakClient, BleakGATTServiceCollection, BleakGATTCharacteristic
from .const import WRITE_CHARACTERISTIC, LOGGER, NOTIFY_CHARACTERISTIC


def getTurnOnCommand():
    return bytearray.fromhex("01 01 01 01".replace(" ", ""))


def getTurnOffCommand():
    return bytearray.fromhex("01 01 01 00".replace(" ", ""))


def getWriteCharacteristic(service: BleakGATTServiceCollection):
    writeCharacteristic = service.get_characteristic(WRITE_CHARACTERISTIC)
    return writeCharacteristic


def getNotifyCharacteristic(service: BleakGATTServiceCollection):
    notifyCharacteristic = service.get_characteristic(NOTIFY_CHARACTERISTIC)
    return notifyCharacteristic


def getLightStateCommand():
    return bytearray.fromhex("00 00 03 11 26 11".replace(" ", ""))


async def sendCommand(
    client: BleakClient, service: BleakGATTServiceCollection, command
):
    await client.write_gatt_char(getWriteCharacteristic(service), command, True)


async def updateEntities(entities):
    for entity in entities:
        LOGGER.warn(entity)
        entity.async_write_ha_state()
        await entity.async_update()


def notification_handler(entryData: dict):
    async def bleak_notification_handler(
        characteristic: BleakGATTCharacteristic, data: bytearray
    ):
        LOGGER.warn("notification_handler")
        LOGGER.warn(data)
        if b"\x00\x00\x02" in data and len(data) == 5:
            state = data[3] == 0x01
            entryData["state"] = state
            entryData["statePending"] = False
            await updateEntities(entryData["entities"])

    return bleak_notification_handler
