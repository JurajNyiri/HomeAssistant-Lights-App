from bleak import BleakClient, BleakGATTServiceCollection, BleakGATTCharacteristic
from .const import WRITE_CHARACTERISTIC, LOGGER, NOTIFY_CHARACTERISTIC
from bleak_retry_connector import BleakClientWithServiceCache


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


def getModeStateCommand():
    return bytearray.fromhex("02 00 00".replace(" ", ""))


def getModeCommand(mode):
    hex_string = "".join(["{:02x}".format(byte) for byte in transformModeToHex(mode)])
    return bytearray.fromhex(("05 01 02 03 " + hex_string).replace(" ", ""))


async def sendCommand(
    client: BleakClient, service: BleakGATTServiceCollection, command
):
    await client.write_gatt_char(getWriteCharacteristic(service), command, True)


async def updateEntities(entities):
    for entity in entities:
        await entity.async_update()
        entity.async_write_ha_state()


def disconnect_handler(entryData: dict):
    def handleBleakDisconnect(client: BleakClientWithServiceCache) -> None:
        LOGGER.warn("handleBleakDisconnect")
        entryData["state"] = None
        entryData["statePending"] = False
        entryData["connection"]["connected"] = False
        for entity in entryData["entities"]:
            entity.async_write_ha_state()

    return handleBleakDisconnect


def transformModeFromHex(hexByte):
    binary_representation = bin(hexByte)[2:][-7:].zfill(7)
    if binary_representation == "0000000":
        binary_representation = "1111111"
    LOGGER.warn(binary_representation)
    bits_array = [int(bit) for bit in binary_representation]
    return {
        "stay_on": bits_array[0] == 1,
        "fast_twinkling": bits_array[1] == 1,
        "fade_away": bits_array[2] == 1,
        "twinkling_in_phase": bits_array[3] == 1,
        "fade_away_in_phase": bits_array[4] == 1,
        "phasing": bits_array[5] == 1,
        "wave": bits_array[6] == 1,
    }


def transformModeToHex(currentMode):
    binaryStr = ""
    for key, value in currentMode.items():
        binaryStr += "1" if value else "0"
    if binaryStr == "0000000":
        binaryStr = "10000000"
    hex_byte = bytearray([int(binaryStr, 2)])
    return hex_byte


def notification_handler(entryData: dict):
    async def bleak_notification_handler(
        characteristic: BleakGATTCharacteristic, data: bytearray
    ):
        LOGGER.warn("notification_handler")
        LOGGER.warn(data)
        # process state
        if b"\x00\x00\x02" in data and len(data) == 5:
            state = data[3] == 0x01
            entryData["state"] = state
            entryData["statePending"] = False
            await updateEntities(entryData["entities"])

        # process mode
        if (
            b"\x02\x00\x0fc\x12\x00\x17;\x00\x00\x00\x00\x00\x00\x00\x00" in data
            and len(data) == 18
        ):
            LOGGER.warn("process mode")
            entryData["mode"] = transformModeFromHex(data[-1])
            LOGGER.warn(entryData["mode"])
            entryData["modePending"] = False
            await updateEntities(entryData["entities"])

    return bleak_notification_handler
