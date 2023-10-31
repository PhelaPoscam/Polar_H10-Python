import asyncio
from bleak import BleakScanner, BleakClient
import FindConnectedDevices


devices =  FindConnectedDevices.find_devices()
address = FindConnectedDevices.get_mac_address("Polar H10", devices)

async def find_devices():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)

asyncio.run(find_devices())

MODEL_NBR_UUID = "2A24"

async def connect(address):
    async with BleakClient(address) as client:
        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        print("Model Number: {0}".format("".join(map(chr, model_number))))

asyncio.run(connect(address))