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


async def sendCommand(
    client: BleakClient, service: BleakGATTServiceCollection, command
):
    await client.write_gatt_char(getWriteCharacteristic(service), command, True)


def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    LOGGER.warn("notification_handler")
    LOGGER.warn(data)
