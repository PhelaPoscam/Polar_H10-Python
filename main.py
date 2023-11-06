import FindConnectedDevices


def main():
    devices = FindConnectedDevices.find_devices()
    address = FindConnectedDevices.get_mac_address("Polar H10", devices)
    print(address)

main()