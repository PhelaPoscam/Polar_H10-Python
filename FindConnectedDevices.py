import subprocess
import platform
import sys
import re

# Install required packages
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'git+https://github.com/pybluez/pybluez.git'])

import bluetooth
def get_connected_devices_linux():
    cmd = "bluetoothctl devices | awk '{print $2}' | while read -r line ; do CONNECTED=$(bluetoothctl info \"$line\" | grep 'Connected: yes') ; if [ -n \"$CONNECTED\" ]; then echo \"Device: $line\" && bluetoothctl info \"$line\" | grep 'Name:' ; fi ; done"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    devices = {}
    for device in result.stdout.split("Device: "):
        if device:
            lines = device.split("\n")
            mac_address = lines[0].strip()
            name = re.search('Name: (.*)', lines[1]).group(1)
            devices[name] = mac_address
    return devices

def get_all_devices_linux():
    cmd = "bluetoothctl devices | awk '{print $2}' | while read -r line ; do echo \"Device: $line\" && bluetoothctl info \"$line\" | grep 'Name:' ; done"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    devices = {}
    for device in result.stdout.split("Device: "):
        if device:
            lines = device.split("\n")
            mac_address = lines[0].strip()
            name_match = re.search('Name: (.*)', lines[1])
            if name_match:
                name = name_match.group(1)
                devices[name] = mac_address
    return devices


def get_connected_devices_windows():
    nearby_devices = bluetooth.discover_devices(lookup_names=True)
    devices = {}
    for addr, name in nearby_devices:
        if bluetooth.BluetoothSocket(bluetooth.RFCOMM).connect_ex((addr, 1)) == 0:
            devices[name] = addr
    return devices

def find_devices():
    if platform.system() == 'Linux':
        devices = get_all_devices_linux()
    elif platform.system() == 'Windows':
        devices = get_connected_devices_windows()
    
    #print('Devices connected:')
    #for name, mac_address in devices.items():
    #    print(f'Name: {name}, MAC Address: {mac_address}')

    return devices
    

def get_mac_address(device_name, devices):
    for name, mac_address in devices.items():
        if device_name.lower() in name.lower():
            return mac_address
    return None