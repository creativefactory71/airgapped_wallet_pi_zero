import json
import os
import time

from keypad_text_entry import enter_number_with_keypad
from display import show_text_highlighted
from button_handler1 import poll_keypad_once

PIN_FILE = "pin.json"

def clear_keypad_buffer():
    """Wait until no button is pressed"""
    print("[DEBUG] Clearing keypad buffer...")
    while True:
        button = poll_keypad_once()
        if button is None:
            break
        time.sleep(0.05)  # 50ms

def save_pin(pin):
    try:
        with open(PIN_FILE, "w") as f:
            json.dump({"pin": pin}, f)
        print(f"[DEBUG] Saved PIN: {pin}")
    except Exception as e:
        print(f"[ERROR] Failed to save PIN: {e}")

def load_pin():
    if not os.path.exists(PIN_FILE):
        print("[DEBUG] No existing PIN file found")
        return None
    try:
        with open(PIN_FILE, "r") as f:
            data = json.load(f)
            print("[DEBUG] Loaded PIN from file")
            return data.get("pin")
    except Exception as e:
        print(f"[ERROR] Failed to load PIN: {e}")
        return None

def setup_or_verify_pin():
    existing_pin = load_pin()

    if existing_pin is None:
        print("[DEBUG] No existing PIN. Starting setup.")
        show_text_highlighted(["No PIN Found", "Set a New PIN"], -1)
        time.sleep(2)

        while True:
            pin = enter_number_with_keypad("Set New PIN")
            print(f"[DEBUG] User entered PIN: {pin}")

            if not pin:
                show_text_highlighted(["Cancelled", "Restarting..."], -1)
                print("[DEBUG] PIN setup cancelled, restarting...")
                time.sleep(2)
                continue

            clear_keypad_buffer()  # <<< VERY IMPORTANT

            confirm_pin = enter_number_with_keypad("Confirm PIN")
            print(f"[DEBUG] User confirmed PIN: {confirm_pin}")

            if not confirm_pin:
                show_text_highlighted(["Cancelled", "Restarting..."], -1)
                print("[DEBUG] PIN confirm cancelled, restarting...")
                time.sleep(2)
                continue

            if pin == confirm_pin and len(pin) >= 4:
                save_pin(pin)
                show_text_highlighted(["PIN Set Successfully", "Starting Wallet..."], -1)
                print("[DEBUG] PIN set successfully.")
                time.sleep(2)
                break
            else:
                show_text_highlighted(["PIN Mismatch or", "Too Short. Try Again"], -1)
                print("[DEBUG] PIN mismatch or too short. Try again.")
                time.sleep(2)

    else:
        print("[DEBUG] Existing PIN found. Starting verification.")
        show_text_highlighted(["Enter Your PIN"], -1)
        time.sleep(1)

        for attempt in range(3):
            pin = enter_number_with_keypad(f"PIN Try {attempt+1}/3")
            print(f"[DEBUG] PIN entered attempt {attempt+1}: {pin}")

            if not pin:
                show_text_highlighted(["Cancelled", "Try Again"], -1)
                print("[DEBUG] Empty PIN entered, retrying...")
                time.sleep(2)
                continue

            if pin == existing_pin:
                show_text_highlighted(["PIN Correct", "Welcome!"], -1)
                print("[DEBUG] Correct PIN entered. Access granted.")
                time.sleep(2)
                return
            else:
                show_text_highlighted(["Wrong PIN!", f"Attempts Left: {2-attempt}"], -1)
                print(f"[DEBUG] Wrong PIN. Attempts left: {2-attempt}")
                time.sleep(2)

        show_text_highlighted(["Too Many Wrong", "Attempts. Exit"], -1)
        print("[DEBUG] Too many wrong attempts. Exiting program.")
        time.sleep(2)
        exit(1)
def reset_pin():
    """Reset the PIN by asking to set a new one."""
    from keypad_text_entry import enter_number_with_keypad
    from display import show_text_highlighted
    import time

    show_text_highlighted(["Reset PIN", "Set a New PIN"], -1)
    time.sleep(2)

    while True:
        pin = enter_number_with_keypad("Set New PIN")
        print(f"[DEBUG] User entered New PIN: {pin}")

        if not pin:
            show_text_highlighted(["Cancelled", "Restarting..."], -1)
            print("[DEBUG] PIN setup cancelled during reset.")
            time.sleep(2)
            continue

        from button_handler1 import poll_keypad_once

        # Clear keypad buffer
        while True:
            button = poll_keypad_once()
            if button is None:
                break
            time.sleep(0.05)

        confirm_pin = enter_number_with_keypad("Confirm New PIN")
        print(f"[DEBUG] User confirmed New PIN: {confirm_pin}")

        if not confirm_pin:
            show_text_highlighted(["Cancelled", "Restarting..."], -1)
            print("[DEBUG] PIN confirm cancelled during reset.")
            time.sleep(2)
            continue

        if pin == confirm_pin and len(pin) >= 4:
            save_pin(pin)
            show_text_highlighted(["New PIN Set", "Successfully!"], -1)
            print("[DEBUG] New PIN saved successfully.")
            time.sleep(2)
            break
        else:
            show_text_highlighted(["PIN Mismatch", "Try Again"], -1)
            print("[DEBUG] PIN mismatch during reset.")
            time.sleep(2)
