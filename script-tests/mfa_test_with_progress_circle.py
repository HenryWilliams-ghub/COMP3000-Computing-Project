#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import sys
import os
sys.path.append('/python/lib/waveshare_epd')
import logging
from PIL import Image, ImageDraw, ImageFont
import random
import string
import time
from pynput import keyboard
from threading import Thread

# Directory setup for fonts and images
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd2in13_V4

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Generates a random MFA code
def get_new_mfa_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

# Updates the e-paper display with the MFA code and input feedback
def update_display(epd, image, draw, font, mfa_code, user_input, feedback):
    draw.rectangle((0, 0, epd.height, epd.width), fill=255)  # Clear the image
    
    # Display the MFA code and feedback
    for i, char in enumerate(mfa_code):
        x = 10 + i * 20
        y = 10
        draw.text((x, y), char, font=font, fill=0)
        if i < len(user_input):
            feedback_char = feedback[i]
            draw.text((x, y + 20), feedback_char, font=font, fill=0)

    # Calculate the progress percentage
    correct_count = sum(1 for i in range(len(feedback)) if feedback[i] == "✓")
    progress_percentage = (correct_count / len(mfa_code)) * 100 if mfa_code else 0
    
    # Draw the progress circle
    progress_circle_x = epd.height - 60
    progress_circle_y = 60
    progress_circle_radius = 45
    progress_circle_inner_radius = 40
    
    draw.ellipse(
        (progress_circle_x - progress_circle_radius, progress_circle_y - progress_circle_radius,
         progress_circle_x + progress_circle_radius, progress_circle_y + progress_circle_radius),
        outline=0, fill=None)
    
    # Fill the progress circle according to the percentage
    fill_angle = int(360 * (progress_percentage / 100))
    draw.pieslice(
        (progress_circle_x - progress_circle_radius, progress_circle_y - progress_circle_radius,
         progress_circle_x + progress_circle_radius, progress_circle_y + progress_circle_radius),
        start=-90, end=-90 + (360 * (progress_percentage / 100)), fill=0)

    # Overlay a smaller white circle to hollow out the pie slice
    draw.ellipse(
        (progress_circle_x - progress_circle_inner_radius, progress_circle_y - progress_circle_inner_radius,
         progress_circle_x + progress_circle_inner_radius, progress_circle_y + progress_circle_inner_radius),
        fill=255) 

    if len(user_input) == len(mfa_code):
        # Check if the entered code is correct
        if user_input == list(mfa_code):
            message = '''Code entered
            successfully!'''
        else:
            message = "Code Incorrect"
        # Clears the display the message
        draw.rectangle((0, 0, epd.height, epd.width), fill=255)
        # Display the message
        message_x = 10
        message_y = 40  # Adjust this value as needed
        draw.text((message_x, message_y), message, font=font, fill=0)
        epd.display(epd.getbuffer(image))
        time.sleep(7)

        draw.rectangle((0, 0, epd.height, epd.width), fill=255)
        epd.display(epd.getbuffer(image))

    else:
        # If the user is still entering the code, update the progress bar
        percentage_text = f"{int(progress_percentage)}%"
        w, h = draw.textsize(percentage_text, font=font)
        draw.text(
            (progress_circle_x - progress_circle_radius / 2, progress_circle_y),
            f"{int(progress_percentage)}%", font=font, fill=0)

    epd.display(epd.getbuffer(image))

# Creates a function to handle key presses
def create_on_press(epd, image, draw, font, mfa_code, user_input, feedback):
    def on_press(key):
        try:
            # Check if the key character is alphanumeric and the user has not finished input
            if hasattr(key, 'char') and key.char:
                char = key.char
                # If caps lock is active or the shift key is held down, the character will be uppercase
                if len(user_input) < len(mfa_code):
                    user_input.append(char)
                    correct = mfa_code[len(user_input) - 1] == char
                    feedback.append("✓" if correct else "✗")
                    update_display(epd, image, draw, font, mfa_code, user_input, feedback)
                if len(user_input) == len(mfa_code):
                    return False
        except Exception as e:
            print(f"Error in on_press: {e}")
    return on_press

try:
    # Initialize and clear the display
    epd = epd2in13_V4.EPD()
    epd.init()
    epd.Clear(0xFF)
      
    # Load font
    font = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)

    # Generate a new MFA code
    mfa_code = get_new_mfa_code()
    user_input = []  # Stores the characters entered by the user
    feedback = []  # Stores feedback for each character entered

    # Create a new blank image and get a drawing context
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)

    # Display the initial MFA code without user input
    update_display(epd, image, draw, font, mfa_code, user_input, feedback)

    # Setup and start listening for keypresses
    listener = keyboard.Listener(on_press=create_on_press(epd, image, draw, font, mfa_code, user_input, feedback))
    listener.start()
    listener.join()
      
except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd2in13_V4.epdconfig.module_exit(cleanup=True)
    sys.exit()
