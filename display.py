import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

# OLED Display Setup
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

# Load Default Font
font = ImageFont.load_default()

def show_text_highlighted(options, selected_idx):
    """
    Displays a menu with highlighted selection on an OLED screen.
    
    Parameters:
    options (list): List of menu options (strings)
    selected_idx (int): Index of the currently selected option (highlighted)
    """
    oled.fill(0)  # Clear display
    image = Image.new("1", (128, 64), "black")
    draw = ImageDraw.Draw(image)

    for i, text in enumerate(options):
        y_position = 10 + (i * 20)  # Adjust vertical positioning
        if i == selected_idx:
            # Draw highlight background
            draw.rectangle((0, y_position - 2, 128, y_position + 12), fill=255)
            # Draw text in black
            draw.text((10, y_position), text, font=font, fill=0)
        else:
            # Normal text in white
            draw.text((10, y_position), text, font=font, fill=255)

    oled.image(image)
    oled.show()
