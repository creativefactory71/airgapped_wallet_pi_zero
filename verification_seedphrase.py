import random
import time
from display import show_text_highlighted

# Updated Mobile keypad mappings
KEYPAD_LETTERS = {
    '1': ['_', ',', '@'],
    '2': ['a', 'b', 'c'],
    '3': ['d', 'e', 'f'],
    '4': ['g', 'h', 'i'],
    '5': ['j', 'k', 'l'],
    '6': ['m', 'n', 'o'],
    '7': ['p', 'q', 'r', 's'],
    '8': ['t', 'u', 'v'],
    '9': ['w', 'x', 'y', 'z']
}

# Special Buttons
DELETE_BUTTON = 'C'
DONE_BUTTON = 'D'
CASE_TOGGLE_BUTTON = '*'

# Timing
LETTER_TIMEOUT = 2.0  # seconds to decide cycle or new letter
DEBOUNCE_TIME = 0.3   # debounce 300ms

# Globals for cycling logic
last_button_pressed = None
last_press_time = 0
current_letter_index = 0
last_button_time = 0

def prepare_seed_verification(wallet_ui):
    print("[DEBUG] Preparing seed phrase verification...")
    word_count = len(wallet_ui.generated_seed_phrase)
    verify_count = 4 if word_count == 12 else 8
    wallet_ui.verification_indices = sorted(random.sample(range(word_count), verify_count))
    wallet_ui.current_verification_index = 0
    wallet_ui.words_verified_count = 0
    wallet_ui.typing_text = ""
    wallet_ui.typing_prompt = ""
    wallet_ui.typing_uppercase = False
    wallet_ui.waiting_for_word_input = True
    print(f"[DEBUG] Selected word indices for verification: {wallet_ui.verification_indices}")

def prompt_for_current_word(wallet_ui):
    idx = wallet_ui.verification_indices[wallet_ui.current_verification_index]
    wallet_ui.typing_prompt = f"Enter word {idx+1}"
    wallet_ui.typing_text = ""
    update_typing_display(wallet_ui)
    wallet_ui.waiting_for_word_input = True

def update_typing_display(wallet_ui):
    lines = [
        wallet_ui.typing_prompt,
        wallet_ui.typing_text,
        "D=Done C=Del *=Caps"
    ]
    show_text_highlighted(lines, -1)

def handle_typing_input(wallet_ui, button):
    global last_button_pressed, last_press_time, current_letter_index, last_button_time

    current_time = time.time()

    button = button.upper()  # <<< UPPERCASE FIX here!

    # Debounce Handling
    if button == last_button_pressed and (current_time - last_button_time) < DEBOUNCE_TIME:
        return  # Ignore bouncing

    last_button_time = current_time

    if button == CASE_TOGGLE_BUTTON:
        wallet_ui.typing_uppercase = not wallet_ui.typing_uppercase
        update_typing_display(wallet_ui)
        return

    elif button == DELETE_BUTTON:
        if len(wallet_ui.typing_text) > 0:
            wallet_ui.typing_text = wallet_ui.typing_text[:-1]
        update_typing_display(wallet_ui)
        return

    elif button == DONE_BUTTON:
        handle_d_press(wallet_ui)
        return

    elif button in KEYPAD_LETTERS:
        if button == last_button_pressed and (current_time - last_press_time) < LETTER_TIMEOUT:
            current_letter_index = (current_letter_index + 1) % len(KEYPAD_LETTERS[button])
            wallet_ui.typing_text = wallet_ui.typing_text[:-1]  # Remove last char
        else:
            current_letter_index = 0  # Reset cycle

        letter = KEYPAD_LETTERS[button][current_letter_index]
        if wallet_ui.typing_uppercase:
            letter = letter.upper()
        wallet_ui.typing_text += letter

        last_press_time = current_time
        last_button_pressed = button

    update_typing_display(wallet_ui)

def handle_d_press(wallet_ui):
    if not wallet_ui.waiting_for_word_input:
        print("[DEBUG] Not waiting for word input. D ignored.")
        return

    typed = wallet_ui.typing_text.strip().lower()
    idx = wallet_ui.verification_indices[wallet_ui.current_verification_index]
    correct_word = wallet_ui.generated_seed_phrase[idx].lower()
    print(f"[DEBUG] Checking entered '{typed}' vs correct '{correct_word}'")

    if typed == correct_word:
        print(f"[VERIFY] Word {idx+1} correct!")
        wallet_ui.words_verified_count += 1
        wallet_ui.current_verification_index += 1

        if wallet_ui.words_verified_count == len(wallet_ui.verification_indices):
            show_text_highlighted(["Verification", "Successful!"], -1)
            time.sleep(2)
            wallet_ui.verification_successful = True  # ✅ SET SUCCESS FLAG
            # ⚡ MenuState change will now happen in main5.py (clean design)
        else:
            prompt_for_current_word(wallet_ui)
    else:
        print(f"[VERIFY] Word {idx+1} incorrect!")
        show_text_highlighted(["Wrong word!", "Restarting..."], -1)
        time.sleep(2)
        wallet_ui.current_verification_index = 0
        wallet_ui.words_verified_count = 0
        prompt_for_current_word(wallet_ui)
