
import FindConnectedDevices
import logging
import pkg_resources
import pip


REQUIRED_PACKAGES = ['pybluez', 'tkinter']

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

import tkinter as tk
from tkinter import ttk

class FindDevicesGUI:
    def __init__(self, master):
        self.master = master
        master.title("Find Connected Devices")

        self.devices = {}

        self.label = ttk.Label(master, text="Select a device:")
        self.label.pack()

        self.device_listbox = tk.Listbox(master)
        self.device_listbox.pack()

        self.refresh_button = ttk.Button(master, text="Refresh", command=self.refresh_devices)
        self.refresh_button.pack()

        self.mac_address_label = ttk.Label(master, text="")
        self.mac_address_label.pack()

        self.quit_button = ttk.Button(master, text="Quit", command=master.quit)
        self.quit_button.pack()

        self.refresh_devices()

    def refresh_devices(self):
        self.devices = FindConnectedDevices.find_devices()
        self.device_listbox.delete(0, tk.END)
        for name in self.devices.keys():
            self.device_listbox.insert(tk.END, name)

    def get_mac_address(self):
        selected_device = self.device_listbox.get(self.device_listbox.curselection())
        mac_address = FindConnectedDevices.get_mac_address(selected_device, self.devices)
        if mac_address:
            self.mac_address_label.config(text=f"MAC Address: {mac_address}")
        else:
            self.mac_address_label.config(text="Device not found")

root = tk.Tk()
my_gui = FindDevicesGUI(root)
root.mainloop()
