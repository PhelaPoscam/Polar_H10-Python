import bluetooth
import logging
import pip
import subprocess
import pkg_resources
import platform
import re

REQUIRED_PACKAGES = ['pybluez']

logger = logging.getLogger(__name__)

def install_package(package):
    try:
        dist = pkg_resources.get_distribution(package)
        logger.info(f'{dist.key} ({dist.version}) is installed')
    except pkg_resources.DistributionNotFound:
        logger.warning(f'{package} is NOT installed')
        pip.main(['install', package])

for package in REQUIRED_PACKAGES:
    install_package(package)

def get_all_devices_linux():
    """
    Returns a dictionary of connected Bluetooth devices on Linux.
    The keys are the device names and the values are the device addresses.
    """
    cmd = (
        "bluetoothctl devices | "
        "awk '{print $2}' | "
        "while read -r line ; do "
        "echo \"Device: $line\" && "
        "bluetoothctl info \"$line\" | "
        "grep 'Name:' ; "
        "done"
    )
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, _ = process.communicate()
    devices = parse_devices(stdout)
    return devices

def parse_devices(output):
    devices = {}
    name_pattern = re.compile('Name: (.*)')
    for device in output.split("Device: "):
        if device:
            lines = device.split("\n")
            mac_address = lines[0].strip()
            name_match = name_pattern.search(lines[1])
            if name_match:
                name = name_match.group(1)
                devices[name] = mac_address
    return devices


import logging
import bluetooth

def get_all_devices_windows():
    """
    Returns a dictionary of connected Bluetooth devices on Windows.
    The keys are the device names and the values are the device addresses.
    """
    logger = logging.getLogger(__name__)
    logger.info("Discovering nearby devices...")
    
    socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    nearby_devices = bluetooth.discover_devices(lookup_names=True)
    devices = {}
    
    for addr, name in nearby_devices:
        logger.info(f"Checking connection for device: {name}")
        
        if name not in devices:
            try:
                with socket as sock:
                    if sock.connect_ex((addr, 1)) == 0:
                        devices[name] = addr
                        logger.info(f"Device connected: {name}")
            except Exception as e:
                logger.error(f'Error connecting to device {name}: {str(e)}')
    
    return devices

def find_devices():
    """
    Finds all connected devices on the system.

    Returns:
    dict: A dictionary containing information about all connected devices.
    """
    devices = {}
    if platform.system() == 'Linux':
        devices = get_all_devices_linux()
    elif platform.system() == 'Windows':
        try:
            devices = get_all_devices_windows()
        except bluetooth.BluetoothError as e:
            logger.error(f'Error connecting to device: {str(e)}')
            devices = {}
    else:
        raise Exception('Unsupported platform')
    return devices
    

def get_mac_address(device_name: str, devices: dict) -> str:
    """
    Get the MAC address of a device given its name.

    Args:
        device_name (str): The name of the device.
        devices (dict): A dictionary containing device names as keys and MAC addresses as values.

    Returns:
        str: The MAC address of the device, or None if the device is not found.
    """
    if not isinstance(device_name, str):
        raise TypeError("device_name must be a string")
    if not isinstance(devices, dict):
        raise TypeError("devices must be a dictionary")

    for name, mac_address in devices.items():
        if device_name.lower() in name.lower():
            return mac_address
    return None

   