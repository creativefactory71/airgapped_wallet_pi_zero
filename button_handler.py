import RPi.GPIO as GPIO
import time
from config import BTN_UP, BTN_DOWN, BTN_ENTER

# Define a debounce delay in seconds
DEBOUNCE_DELAY = 0.5  
last_pressed_time = {"UP": 0, "DOWN": 0, "ENTER": 0}

def setup_buttons():
    """Initialize GPIO buttons"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BTN_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BTN_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BTN_ENTER, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def poll_buttons(callback):
    """Continuously poll button states and trigger callback with debounce"""
    while True:
        current_time = time.time()
        
        if GPIO.input(BTN_UP) == GPIO.LOW and (current_time - last_pressed_time["UP"]) > DEBOUNCE_DELAY:
            last_pressed_time["UP"] = current_time
            # print("BTN_UP pressed")  # Debug print
            callback("UP")

        elif GPIO.input(BTN_DOWN) == GPIO.LOW and (current_time - last_pressed_time["DOWN"]) > DEBOUNCE_DELAY:
            last_pressed_time["DOWN"] = current_time
            # print("BTN_DOWN pressed")  # Debug print
            callback("DOWN")

        elif GPIO.input(BTN_ENTER) == GPIO.LOW and (current_time - last_pressed_time["ENTER"]) > DEBOUNCE_DELAY:
            last_pressed_time["ENTER"] = current_time
            # print("BTN_ENTER pressed")  # Debug print
            callback("ENTER")

        time.sleep(0.1)  # Small delay to prevent high CPU usage
