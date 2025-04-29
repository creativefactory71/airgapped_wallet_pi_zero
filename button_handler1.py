import time
import board
import digitalio
import adafruit_matrixkeypad

# Keypad pin setup
ROW_PINS = [digitalio.DigitalInOut(x) for x in (board.D5, board.D6, board.D13, board.D19)]
COL_PINS = [digitalio.DigitalInOut(x) for x in (board.D12, board.D16, board.D20, board.D21)]

keys = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

keypad = adafruit_matrixkeypad.Matrix_Keypad(ROW_PINS, COL_PINS, keys)

# Debounce tracking
last_pressed = None
last_time = 0
DEBOUNCE_TIME = 0.3  # seconds

def poll_keypad(callback):
    """Poll the keypad continuously and send keypresses to callback."""
    global last_pressed, last_time
    while True:
        pressed = keypad.pressed_keys
        current_time = time.time()

        if pressed:
            key = pressed[0]

            # Debounce logic
            if key != last_pressed or (current_time - last_time) > DEBOUNCE_TIME:
                last_pressed = key
                last_time = current_time
                callback(key)

        time.sleep(0.1)

def poll_keypad_once():
    """Poll the keypad once and return the key if pressed, otherwise None."""
    pressed = keypad.pressed_keys
    if pressed:
        return pressed[0]
    else:
        return None
