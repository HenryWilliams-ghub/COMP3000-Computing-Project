#!/usr/bin/env python3
import evdev
import time

NULL_CHAR = chr(0)

def write_report(report):
    with open('/dev/hidg0', 'rb+') as fd:
        fd.write(report.encode())
              
device = evdev.InputDevice('/dev/input/event0')
print(device)

while 1:
    for key in device.active_keys():
        if key == 30:
            #'\x00\x00\x04\x00\x00\x00\x00\x00'
            write_report(NULL_CHAR*2+chr(4)+NULL_CHAR*5)
            write_report(NULL_CHAR*8)
        write_report(NULL_CHAR*8)
