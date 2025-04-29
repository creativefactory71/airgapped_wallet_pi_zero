# keypad_text_entry.py

import time
from display import show_text_highlighted
from button_handler1 import poll_keypad_once

# Mobile keypad style mappings (only small letters here)
KEYPAD_LETTERS = {
    '1': ['_', ',', '@', '1'],
    '2': ['a', 'b', 'c', '2'],
    '3': ['d', 'e', 'f', '3'],
    '4': ['g', 'h', 'i', '4'],
    '5': ['j', 'k', 'l', '5'],
    '6': ['m', 'n', 'o', '6'],
    '7': ['p', 'q', 'r', 's', '7'],
    '8': ['t', 'u', 'v', '8'],
    '9': ['w', 'x', 'y', '9'],
    '0': ['0'],
}

# Special buttons
DELETE_BUTTON = 'C'
DONE_BUTTON = 'D'
CASE_TOGGLE_BUTTON = '*'

LETTER_TIMEOUT = 2.0  # seconds to decide next letter or new letter
DEBOUNCE_TIME = 0.3   # debounce 300ms (adjustable)

def enter_text_with_keypad(prompt="Enter Text"):
    text = ""
    current_key = None
    current_index = 0
    last_press_time = time.time()
    last_button_time = 0  # NEW: for debounce
    last_button = None
    is_uppercase = False  # start with lowercase

    while True:
        display_line = [prompt, text, "D=Done C=Del *=Caps"]
        show_text_highlighted(display_line, -1)

        button = poll_keypad_once()
        current_time = time.time()

        if button is None:
            continue

        # DEBOUNCE HANDLING:
        if button == last_button and (current_time - last_button_time) < DEBOUNCE_TIME:
            continue  # Ignore bouncing
        last_button = button
        last_button_time = current_time

        # NORMAL HANDLING:
        if button == CASE_TOGGLE_BUTTON:
            is_uppercase = not is_uppercase  # Toggle case
            continue

        if button == DELETE_BUTTON:
            if len(text) > 0:
                text = text[:-1]
            current_key = None
            continue

        if button == DONE_BUTTON:
            return text

        if button in KEYPAD_LETTERS:
            if button == current_key and (current_time - last_press_time) < LETTER_TIMEOUT:
                # Cycle to next letter
                current_index = (current_index + 1) % len(KEYPAD_LETTERS[button])
                text = text[:-1]  # remove last letter to replace
            else:
                current_index = 0  # reset cycle

            letter = KEYPAD_LETTERS[button][current_index]
            if is_uppercase:
                letter = letter.upper()

            text += letter

            current_key = button
            last_press_time = current_time

def enter_number_with_keypad(prompt="Enter Number"):
    number = ""
    last_button_time = 0
    last_button = None

    while True:
        display_line = [prompt, number, "D=Done C=Del"]
        show_text_highlighted(display_line, -1)

        button = poll_keypad_once()
        current_time = time.time()

        if button is None:
            continue

        # DEBOUNCE HANDLING:
        if button == last_button and (current_time - last_button_time) < DEBOUNCE_TIME:
            continue  # Ignore bouncing
        last_button = button
        last_button_time = current_time

        # NORMAL HANDLING:
        if button.isdigit():
            number += button

        elif button == DELETE_BUTTON:
            if len(number) > 0:
                number = number[:-1]

        elif button == DONE_BUTTON:
            return number
