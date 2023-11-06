import asyncio
#from pylsl import StreamInfo, StreamOutlet

from numpy import mean
import FindConnectedDevices
import asyncio
import time

from bleak import BleakClient
from bleak.uuids import uuid16_dict

devices =  FindConnectedDevices.find_devices()
address = FindConnectedDevices.get_mac_address("Polar H10", devices)

uuid16_dict = {v: k for k, v in uuid16_dict.items()}
MODEL_NBR_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Model Number String")
)
MANUFACTURER_NAME_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Manufacturer Name String")
)
BATTERY_LEVEL_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Battery Level")
)
## UUID for connection establishment with device ##
PMD_SERVICE = "FB005C80-02E7-F387-1CAD-8ACD2D8DF0C8"

## UUID for Request of stream settings ##
PMD_CONTROL = "FB005C81-02E7-F387-1CAD-8ACD2D8DF0C8"

## UUID for Request of start stream ##
PMD_DATA = "FB005C82-02E7-F387-1CAD-8ACD2D8DF0C8"

## UUID for Request of ECG Stream ##
ECG_WRITE = bytearray([0x02, 0x00, 0x00, 0x01, 0x82, 0x00, 0x01, 0x01, 0x0E, 0x00])

## For Polar H10  sampling frequency ##
ECG_SAMPLING_FREQ = 130

OUTLET = []

def data_conv(sender, data: bytearray):
    #global OUTLET
    if data[0] == 0x00:
        print(".", end = '', flush=True)
        step = 3
        samples = data[10:]
        offset = 0
        while offset < len(samples):
            ecg = convert_array_to_signed_int(samples, offset, step)
            offset += step
            OUTLET.push_sample([ecg])
            

def convert_array_to_signed_int(data, offset, length):
    return int.from_bytes(
        bytearray(data[offset : offset + length]), byteorder="little", signed=True,
    )


def convert_to_unsigned_long(data, offset, length):
    return int.from_bytes(
        bytearray(data[offset : offset + length]), byteorder="little", signed=False,
    )

# def data_conv(sender, data: bytearray):
#     #global OUTLET
#     if data[0] == 0x00:
#         print(".", end = '', flush=True)
#         step = 3
#         samples = data[10:]
#         offset = 0
#         while offset < len(samples):
#             ecg = convert_array_to_signed_int(samples, offset, step)
#             offset += step
#             OUTLET.push_sample([ecg])

# #def StartStream(STREAMNAME):

#     info = StreamInfo(STREAMNAME, 'ECG', 1,ECG_SAMPLING_FREQ, 'float32', 'myuid2424')

#     info.desc().append_child_value("manufacturer", "Polar")
#     channels = info.desc().append_child("channels")
#     for c in ["ECG"]:
#         channels.append_child("channel")\
#             .append_child_value("name", c)\
#             .append_child_value("unit", "microvolts")\
#             .append_child_value("type", "ECG")

#     return StreamOutlet(info, 74, 360)

async def run(address):
    client = BleakClient(address)
    if not client.is_connected:
        await client.connect()
    print(f"Connected: {client.is_connected}")

    model_number = await client.read_gatt_char(MODEL_NBR_UUID)
    print("Model Number: {0}".format("".join(map(chr, model_number))), flush=True)
    manufacturer_name = await client.read_gatt_char(MANUFACTURER_NAME_UUID)
    print("Manufacturer Name: {0}".format("".join(map(chr, manufacturer_name))), flush=True)
    battery_level = await client.read_gatt_char(BATTERY_LEVEL_UUID)
    print("Battery Level: {0}%".format(int(battery_level[0])), flush=True)


    heart_rates = []

    def callback(sender: int, data: bytearray):
        heart_rate = int.from_bytes(data[1:2], byteorder="little")
        print("Heart Rate: {0}".format(heart_rate))
        timestamp = time.time()
        heart_rates.append((timestamp, heart_rate))

    await client.start_notify("00002a37-0000-1000-8000-00805f9b34fb", callback)
    await asyncio.sleep(5.0)
    await client.stop_notify("00002a37-0000-1000-8000-00805f9b34fb")

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))