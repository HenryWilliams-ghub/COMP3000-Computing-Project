import RPi.GPIO as GPIO
import time
import random
import string
from waveshare_epd import epd2in13_V2
from PIL import Image, ImageDraw, ImageFont

# Generate a random 6-character code
def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Initialize the e-Paper display
def init_display():
    epd = epd2in13_V2.EPD()
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)
    return epd

# Draw progress bar
def draw_progress_bar(draw, x, y, width, height, progress, max_progress):
    # Draw the outline
    draw.rectangle((x, y, x+width, y+height), outline=0)
    # Calculate the width of the inside "filled" part
    filled_width = int((progress / max_progress) * width)
    # Draw the filled part
    draw.rectangle((x, y, x+filled_width, y+height), fill=0)
    # Calculate and display the percentage
    percentage = int((progress / max_progress) * 100)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
    draw.text((x + width/2, y + height/2 - 6), f'{percentage}%', font=font, fill=255, anchor="mm")

# Display code, progress bar, and prompt for user input
def display_code_and_prompt(epd, code):
    font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
    font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 12)
    image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)

    # Display the code
    draw.text((10, 10), f'Code: {code}', font=font_large, fill=0)

    # Initialize progress
    progress = 0
    max_progress = len(code)  # Assuming each character correctly entered increases progress

    # Display initial progress bar
    draw_progress_bar(draw, 10, 50, 200, 20, progress, max_progress)

    epd.display(epd.getbuffer(image.rotate(90, expand=True)))

    # Wait for user input and validate
    for char in code:
        entered_char = input("Enter the next character of the code: ")
        if entered_char == char:
            progress += 1
            # Redraw progress bar with updated progress
            draw_progress_bar(draw, 10, 50, 200, 20, progress, max_progress)
            epd.display(epd.getbuffer(image.rotate(90, expand=True)))
        else:
            print("Incorrect character. Try the next one.")

    if progress == max_progress:
        print("Code correct")
    else:
        print("Code incorrect")

# Main function
def main():
    try:
        epd = init_display()
        code = generate_code()
        display_code_and_prompt(epd, code)

    except IOError as e:
        print(e)

    except KeyboardInterrupt:
        print("Exiting...")
        epd2in13_V2.epdconfig.module_exit()
        exit()

if __name__ == "__main__":
    main()
