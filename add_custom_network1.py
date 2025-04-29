# add_custom_network1.py

import json
import time
from display import show_text_highlighted
from keypad_text_entry import enter_text_with_keypad, enter_number_with_keypad

CUSTOM_NETWORK_FILE = "custom_network.json"

def load_custom_network():
    try:
        with open(CUSTOM_NETWORK_FILE, "r") as f:
            custom_networks = json.load(f)
            print(f"[INFO] Loaded custom networks: {custom_networks}")
            return custom_networks  # return list
    except (FileNotFoundError, json.JSONDecodeError):
        print("[INFO] No custom networks found")
        return []

def add_custom_network_interactively(wallet_ui_instance):
    print("[ACTION] Adding Custom Network")

    # 1. Input Coin Name
    network_name = enter_text_with_keypad("Enter Coin Name")
    if not network_name.strip() or len(network_name.strip()) < 2:
        show_text_highlighted(["Invalid Name", "Try Again"], -1)
        time.sleep(2)
        wallet_ui_instance.update_home_display()
        return

    network_name = network_name.strip().upper()  # ✅ Automatically convert to UPPERCASE

    # 2. Inform user
    show_text_highlighted(["Coin Name Saved", "Enter Chain ID"], -1)
    time.sleep(2)

    # 3. Input Chain ID
    chain_id_input = enter_number_with_keypad("Enter Chain ID")
    if not chain_id_input:
        show_text_highlighted(["Invalid Chain ID", "Try Again"], -1)
        time.sleep(2)
        wallet_ui_instance.update_home_display()
        return

    try:
        chain_id = int(chain_id_input)
    except ValueError:
        show_text_highlighted(["Invalid Chain ID", "Try Again"], -1)
        time.sleep(2)
        wallet_ui_instance.update_home_display()
        return

    # 4. Create new network entry
    new_network = {
        "name": network_name,
        "chain_id": chain_id
    }

    # 5. Load existing networks
    try:
        existing_networks = load_custom_network()
    except:
        existing_networks = []

    # 6. Append new network
    existing_networks.append(new_network)

    # 7. Save back to file
    try:
        with open(CUSTOM_NETWORK_FILE, "w") as f:
            json.dump(existing_networks, f, indent=4)
        print("[INFO] Custom network added and saved")
    except Exception as e:
        print(f"[ERROR] Failed to save custom network: {e}")
        show_text_highlighted(["Save Failed"], -1)
        time.sleep(2)
        wallet_ui_instance.update_home_display()
        return

    # 8. Update wallet UI instance
    wallet_ui_instance.custom_network = existing_networks

    # 9. Show success
    show_text_highlighted(["Custom Network", "Added Successfully"], -1)
    time.sleep(2)
    wallet_ui_instance.update_home_display()
