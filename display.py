import digitalio
import board
import busio

from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735

# === TFT Display Setup (SPI)
WIDTH = 160
HEIGHT = 128

spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)
dc = digitalio.DigitalInOut(board.D24)
reset = digitalio.DigitalInOut(board.D25)

disp = st7735.ST7735R(spi, cs=cs, dc=dc, rst=reset,
                      width=128, height=160,
                      rotation=90, bgr=True)

# === Font (Smaller)
try:
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 12)  # Smaller size
except:
    font = ImageFont.load_default()

def show_qr_on_display(qr_img):
    """
    Resize and display a monochrome QR image on the ST7735 RGB display.
    """
    resized_qr = qr_img.resize((WIDTH, HEIGHT), Image.NEAREST).convert("RGB")
    disp.image(resized_qr)

def show_text_highlighted(options, selected_idx):
    """
    Displays a menu with highlighted selection on the ST7735 TFT screen.
    
    Parameters:
    options (list): List of menu options (strings)
    selected_idx (int): Index of the currently selected option (highlighted)
    """
    image = Image.new("RGB", (WIDTH, HEIGHT), "black")
    draw = ImageDraw.Draw(image)

    y_offset = 10     # Starting Y position
    spacing = 20      # Distance between lines

    for i, text in enumerate(options):
        y_position = y_offset + (i * spacing)
        if i == selected_idx:
            # Highlighted selection (blue background)
            draw.rectangle((0, y_position - 2, WIDTH, y_position + 14), fill=(0, 120, 255))
            draw.text((10, y_position), text, font=font, fill=(0, 0, 0))  # Black text
        else:
            draw.text((10, y_position), text, font=font, fill=(255, 255, 255))  # White text

    disp.image(image)

# === Example Usage ===
if __name__ == "__main__":
    menu_options = ["Create Wallet", "Restore Wallet", "Send TX", "Settings", "About", "Exit"]
    selected_index = 2  # Example: highlight "Send TX"

    show_text_highlighted(menu_options, selected_index)
