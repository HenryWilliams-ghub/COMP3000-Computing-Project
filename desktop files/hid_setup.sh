#!/bin/bash

# Load libcomposite
modprobe libcomposite

# Create the gadget directory
cd /sys/kernel/config/
mkdir usb_gadget
cd /sys/kernel/config/usb_gadget/
mkdir -p g1
cd g1

# Set Vendor and Product IDs
echo 0x1d6b > idVendor # Linux Foundation
echo 0x0104 > idProduct # Multifunction Composite Gadget

# Set USB version and device version
echo 0x0200 > bcdUSB # USB 2.0
echo 0x0100 > bcdDevice # Version 1.0.0

# Define the device's strings
mkdir -p strings/0x409
echo "10000000c375c7e1" > strings/0x409/serialnumber
echo "Sony" > strings/0x409/manufacturer
echo "Raspberry Pi 4 Model B Rev 1.5" > strings/0x409/product

# Create a configuration instance
mkdir -p configs/c.1/strings/0x409
echo "Config 1: Keyboard" > configs/c.1/strings/0x409/configuration
echo 250 > configs/c.1/MaxPower

# Create the HID function
mkdir -p functions/hid.usb0
echo 1 > functions/hid.usb0/protocol
echo 1 > functions/hid.usb0/subclass
echo 8 > functions/hid.usb0/report_length
echo -ne \\x05\\x01\\x09\\x06\\xa1\\x01\\x05\\x07\\x19\\xe0\\x29\\xe7\\x15\\x00\\x25\\x01\\x75\\x01\\x95\\x08\\x81\\x02\\x95\\x01\\x75\\x08\\x81\\x01\\x95\\x05\\x75\\x01\\x05\\x08\\x19\\x01\\x29\\x05\\x91\\x02\\x95\\x01\\x75\\x03\\x91\\x01\\x95\\x06\\x75\\x08\\x15\\x00\\x25\\x65\\x05\\x07\\x19\\x00\\x29\\x65\\x81\\x00\\xc0 > functions/hid.usb0/report_desc

# Link HID function to the configuration
ln -s functions/hid.usb0 configs/c.1/

# Bind the USB gadget to the first available UDC
ls /sys/class/udc > UDC

echo "USB HID gadget set up complete."