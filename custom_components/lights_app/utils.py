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


def getBrightnessCommand(brightness):
    if 10 <= brightness < 100:
        hex_string = f"03 01 01 {brightness:02x}"
        return bytearray.fromhex(hex_string.replace(" ", ""))
    raise Exception(
        "Invalid brightness. Brightness has to be larger than 10 and smaller than 100."
    )


def get_brightness_from_bytearray(byte_array):
    # Assuming brightness value is always at the 4th index (0-based).
    # Since the bytearray represents the brightness in a single byte, we treat it as a number already in decimal.
    brightness_value = byte_array[3]
    # Convert the decimal brightness value to hexadecimal and remove the '0x' prefix
    brightness_hex = hex(brightness_value)[2:]
    # Convert the hexadecimal value back to decimal
    brightness_decimal = int(brightness_hex, 16)
    return brightness_decimal


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
        LOGGER.debug("handleBleakDisconnect")
        entryData["state"] = None
        entryData["statePending"] = False
        entryData["mode"] = None
        entryData["modePending"] = False
        entryData["brightness"] = None
        entryData["brightnessPending"] = False
        entryData["connection"]["connected"] = False
        for entity in entryData["entities"]:
            entity.async_write_ha_state()

    return handleBleakDisconnect


def transformModeFromHex(hexByte):
    binary_representation = bin(hexByte)[2:][-7:].zfill(7)
    if binary_representation == "0000000":
        binary_representation = "1111111"
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
        LOGGER.debug("notification_handler")
        LOGGER.debug(data)
        # process state
        if b"\x00\x00\x02" in data and len(data) == 5:
            state = data[3] == 0x01
            entryData["state"] = state
            entryData["statePending"] = False
            await updateEntities(entryData["entities"])

        # process mode and brightness data
        if b"\x00\x00\x00\x00\x00\x00\x00\x00" in data and len(data) == 18:
            entryData["mode"] = transformModeFromHex(data[-1])
            entryData["brightness"] = get_brightness_from_bytearray(data)
            LOGGER.debug(
                "State of brightness changed to: " + str(entryData["brightness"])
            )
            entryData["modePending"] = False
            entryData["brightnessPending"] = False
            await updateEntities(entryData["entities"])

    return bleak_notification_handler
