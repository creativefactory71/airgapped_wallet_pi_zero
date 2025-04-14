import time
import board
import digitalio
import busio
from PIL import Image, ImageDraw, ImageFont

# Display
import adafruit_rgb_display.st7735 as st7735

# Keypad
import adafruit_matrixkeypad

# === Display Setup
WIDTH = 160
HEIGHT = 128

spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D8)
dc = digitalio.DigitalInOut(board.D24)
reset = digitalio.DigitalInOut(board.D25)

disp = st7735.ST7735R(spi, cs=cs, dc=dc, rst=reset,
                      width=128, height=160,
                      rotation=90, bgr=True)

# === Font
try:
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 24)
except:
    font = ImageFont.load_default()

# === Keypad Setup
# Define rows and columns based on GPIOs
ROW_PINS = [digitalio.DigitalInOut(x) for x in (board.D5, board.D6, board.D13, board.D19)]
COL_PINS = [digitalio.DigitalInOut(x) for x in (board.D12, board.D16, board.D20, board.D21)]

keys = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

keypad = adafruit_matrixkeypad.Matrix_Keypad(ROW_PINS, COL_PINS, keys)

# === Display Function
def display_text(text):
    image = Image.new("RGB", (WIDTH, HEIGHT), "black")
    draw = ImageDraw.Draw(image)
    draw.text((10, 50), text, font=font, fill=(255, 255, 255))
    disp.image(image)

# === Main Loop
buffer = ""
display_text("Press Key")

while True:
    keys = keypad.pressed_keys
    if keys:
        for key in keys:
            buffer += key
            display_text(buffer)
        time.sleep(0.3)  # debounce delay
