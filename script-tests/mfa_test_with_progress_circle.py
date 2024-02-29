#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
sys.path.append('/python/lib/waveshare_epd')
from waveshare_epd import epd2in13_V4
import logging
from PIL import Image, ImageDraw, ImageFont
import random
import string
from pynput import keyboard
from threading import Thread

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
        feedback_char = feedback[i] if i < len(feedback) else ' '
        draw.text((x, y + 20), feedback_char, font=font, fill=0)

    # Calculate the progress percentage
    correct_count = sum(1 for i in range(len(feedback)) if feedback[i] == "✓")
    progress_percentage = (correct_count / len(mfa_code)) * 100 if mfa_code else 0
    
    # Draw the progress circle
    progress_circle_x = epd.height - 30
    progress_circle_y = 10
    progress_circle_radius = 15
    draw.ellipse(
        (progress_circle_x - progress_circle_radius, progress_circle_y - progress_circle_radius,
         progress_circle_x + progress_circle_radius, progress_circle_y + progress_circle_radius),
        outline=0, fill=None)
    # Fill the progress circle according to the percentage
    fill_angle = int(360 * (progress_percentage / 100))
    draw.pieslice(
        (progress_circle_x - progress_circle_radius, progress_circle_y - progress_circle_radius,
         progress_circle_x + progress_circle_radius, progress_circle_y + progress_circle_radius),
        start=0, end=fill_angle, fill=0)
    # Display the percentage text
    draw.text(
        (progress_circle_x - progress_circle_radius / 2, progress_circle_y),
        f"{int(progress_percentage)}%", font=font, fill=0)

    epd.display(epd.getbuffer(image))

# Creates a function to handle key presses
def create_on_press(epd, image, draw, font, mfa_code, user_input, feedback):
    def on_press(key):
        try:
            if hasattr(key, 'char') and key.char and len(user_input) < len(mfa_code):
                char = key.char
                user_input.append(char)
                # Check if the input matches the corresponding character in the MFA code
                correct = mfa_code[len(user_input) - 1] == char
                feedback.append("✓" if correct else "✗")
                update_display(epd, image, draw, font, mfa_code, user_input, feedback)

            # Stop the listener once the full code has been entered
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
