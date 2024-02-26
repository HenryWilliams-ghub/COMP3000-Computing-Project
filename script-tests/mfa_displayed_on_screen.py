#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import time
from datetime import datetime
import logging
from PIL import Image, ImageDraw, ImageFont
import traceback
import random
import string


# Import the necessary library for the e-Paper display
from waveshare_epd import epd2in13_V4

# Directory setup for fonts and images
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

logging.basicConfig(level=logging.DEBUG)

def get_new_mfa_code(length=6):
# Generates a random string of letters and digits
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

# Generate and display the code
code = generate_random_code()
print(f"Your code is: {code}")

def draw_progress_bar(draw, width, height, progress):
    # Function to draw the progress bar
    x0, y0, x1, y1 = 10, height - 20, width - 10, height - 10
    draw.rectangle((x0, y0, x1, y1), outline=0, fill=255)  # Draw the progress bar background
    fill_width = int((x1 - x0) * progress)
    draw.rectangle((x0, y0, x0 + fill_width, y1), outline=0, fill=0)  # Fill the progress

def update_display(epd, image, draw, font, mfa_code, user_input):
    # Clear the image for the next drawing
    draw.rectangle((0, 0, epd.height, epd.width), fill=255)

    # Display the MFA code with feedback
    for i, char in enumerate(mfa_code):
        if i < len(user_input):
            fill = 0 if mfa_code[i] == user_input[i] else 255
            draw.rectangle([10 + i*20, 10, 30 + i*20, 30], fill=fill)
            draw.text((10 + i*20, 10), char, font=font, fill=255-fill)
        else:
            draw.text((10 + i*20, 10), char, font=font, fill=0)

    # Update the e-Paper display
    epd.display(epd.getbuffer(image))

try:
    epd = epd2in13_V4.EPD()
    epd.init()
    epd.Clear(0xFF)

    font = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)

    mfa_code = get_new_mfa_code()
    user_input = ''

    # Create a new blank image and get a drawing context
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)

    while len(user_input) < len(mfa_code):
        update_display(epd, image, draw, font, mfa_code, user_input)
        char = input("Enter next character: ")
        if len(char) == 1 and char.isalnum():
            user_input += char

    print("You've entered the MFA code.")

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in13_V4.epdconfig.module_exit(cleanup=True)
    exit()
