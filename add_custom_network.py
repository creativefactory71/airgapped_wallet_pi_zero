import json
import time
from display import show_text_highlighted

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

    network_name = input("Enter Network Name: ").strip()
    chain_id_input = input("Enter Chain ID (number only): ").strip()

    try:
        chain_id = int(chain_id_input)
    except ValueError:
        print("[ERROR] Invalid Chain ID")
        show_text_highlighted(["Invalid Chain ID", "Try Again"], -1)
        time.sleep(2)
        wallet_ui_instance.update_home_display()
        return

    new_network = {
        "name": network_name,
        "chain_id": chain_id
    }

    # Load existing networks
    try:
        existing_networks = load_custom_network()
    except:
        existing_networks = []

    # Append new network
    existing_networks.append(new_network)

    # Save back to file
    try:
        with open(CUSTOM_NETWORK_FILE, "w") as f:
            json.dump(existing_networks, f)
        print("[INFO] Custom network added and saved")
    except Exception as e:
        print(f"[ERROR] Failed to save custom network: {e}")

    # Update wallet UI instance
    wallet_ui_instance.custom_network = existing_networks

    show_text_highlighted(["Custom Network", "Added Successfully"], -1)
    time.sleep(2)
    wallet_ui_instance.update_home_display()
