#!/usr/bin/env python3
import evdev
from evdev import ecodes, InputDevice, categorize
import time

NULL_CHAR = chr(0)

def write_report(fd, report):
    try:
        fd.write(report.encode())
    except BlockingIOError:
        print("BlockingIOError caught. Trying again...")
        time.sleep(0.1)  # Adjust delay as necessary
        write_report(fd, report)

device = InputDevice('/dev/input/event0')
print(device)

key_states = {}  # Tracks the state of each key

# HID  ID mapping for keys

key_mapping = {
    ecodes.KEY_A: 4,  # 'a'
    ecodes.KEY_B: 5,  # 'b'
    ecodes.KEY_C: 6,  # 'c'
    ecodes.KEY_D: 7,  # 'd'
    ecodes.KEY_E: 8,  # 'e'
    ecodes.KEY_F: 9,  # 'f'
    ecodes.KEY_G: 10, # 'g'
    ecodes.KEY_H: 11, # 'h'
    ecodes.KEY_I: 12, # 'i'
    ecodes.KEY_J: 13, # 'j'
    ecodes.KEY_K: 14, # 'k'
    ecodes.KEY_L: 15, # 'l'
    ecodes.KEY_M: 16, # 'm'
    ecodes.KEY_N: 17, # 'n'
    ecodes.KEY_O: 18, # 'o'
    ecodes.KEY_P: 19, # 'p'
    ecodes.KEY_Q: 20, # 'q'
    ecodes.KEY_R: 21, # 'r'
    ecodes.KEY_S: 22, # 's'
    ecodes.KEY_T: 23, # 't'
    ecodes.KEY_U: 24, # 'u'
    ecodes.KEY_V: 25, # 'v'
    ecodes.KEY_W: 26, # 'w'
    ecodes.KEY_X: 27, # 'x'
    ecodes.KEY_Y: 28, # 'y'
    ecodes.KEY_Z: 29, # 'z'
    ecodes.KEY_1: 30, # '1' and '!'
    ecodes.KEY_2: 31, # '2' and '@'
    ecodes.KEY_3: 32, # '3' and '#'
    ecodes.KEY_4: 33, # '4' and '$'
    ecodes.KEY_5: 34, # '5' and '%'
    ecodes.KEY_6: 35, # '6' and '^'
    ecodes.KEY_7: 36, # '7' and '&'
    ecodes.KEY_8: 37, # '8' and '*'
    ecodes.KEY_9: 38, # '9' and '('
    ecodes.KEY_0: 39, # '0' and ')'
    # Symbols and special characters
    ecodes.KEY_SPACE: 44,        # Space
    ecodes.KEY_MINUS: 45,        # '-' and '_'
    ecodes.KEY_EQUAL: 46,        # '=' and '+'
    ecodes.KEY_LEFTBRACE: 47,    # '[' and '{'
    ecodes.KEY_RIGHTBRACE: 48,   # ']' and '}'
    ecodes.KEY_BACKSLASH: 49,    # '\' and '|'
    ecodes.KEY_SEMICOLON: 51,    # ';' and ':'
    ecodes.KEY_APOSTROPHE: 52,   # '\'' and '"'
    ecodes.KEY_GRAVE: 53,        # '`' and '~'
    ecodes.KEY_COMMA: 54,        # ',' and '<'
    ecodes.KEY_DOT: 55,          # '.' and '>'
    ecodes.KEY_SLASH: 56,        # '/' and '?'
    
    
}
# Open /dev/hidg0 outside of the loop
with open('/dev/hidg0', 'rb+', buffering=0) as fd:
    while True:
        for event in device.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                if key_event.keystate in (key_event.key_down, key_event.key_hold):
                    if event.code in key_mapping:
                        hid_code = key_mapping[event.code]
                        if 0 <= hid_code <= 255:
                            report = NULL_CHAR*2 + chr(hid_code) + NULL_CHAR*5
                            write_report(fd, report)
                            key_states[event.code] = True
                elif key_event.keystate == key_event.key_up:
                    if event.code in key_states and key_states[event.code]:
                        write_report(fd, NULL_CHAR*8)
                        key_states[event.code] = False