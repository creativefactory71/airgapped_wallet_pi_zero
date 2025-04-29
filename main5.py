import time
import json
import os
import qrcode

from blockchain_config import load_blockchain_config
from display import show_text_highlighted, show_qr_on_display
from button_handler import poll_keypad
from wallet_generator import generate_wallet
from restore_wallet import regenerate_wallet
from final_offline_tx_generator import generate_offline_transaction
from qr_scanner import scan_qr_code
from sign_transaction import sign_transaction
from add_custom_network1 import load_custom_network, add_custom_network_interactively
from pin_manager import setup_or_verify_pin
# Import verification functions
from verification_seedphrase import (
    prepare_seed_verification,
    prompt_for_current_word,
    handle_typing_input,
    update_typing_display
)

class MenuState:
    SPLASH = 0
    MAIN = 1
    CREATE_WALLET = 2
    RESTORE_WALLET = 3
    DISPLAY_SEED = 4
    VERIFY_SEED = 5
    HOME_SCREEN = 6
    SELECT_COIN = 7
    SEND_TRANSACTION_INPUT = 8
    CONFIRM_DELETE = 9
class WalletUI:
    def __init__(self):
        self.current_state = MenuState.SPLASH
        self.selected_option = 0

        self.generated_wallet = {}
        self.generated_seed_phrase = []
        self.entered_seed_phrase = []
        self.seed_screen_index = 0
        self.verification_successful = False
        self.main_menu = ["Create Wallet", "Restore Wallet"]
        self.wallet_menu = ["12 words", "24 words", "Back"]
        self.restore_menu = ["12 words", "24 words", "Back"]
        self.coin_options = ["XDC", "Ethereum"]
        self.home_screen_options = [
            "Send Transaction", "Receive Transaction",
            "Add Custom Network", "Settings",
            "Device Info", "Delete My Account", "Back"
        ]

        self.selected_coin = "XDC"
        self.tx_input_field = "receiver"
        self.tx_receiver = ""
        self.tx_amount = ""
        self.tx_nonce = ""

        self.custom_network = None

        # Typing related for verification
        self.typing_text = ""
        self.typing_prompt = ""
        self.typing_uppercase = False
        self.waiting_for_word_input = False

        # Verification state
        self.verification_indices = []
        self.current_verification_index = 0
        self.words_verified_count = 0
    def show_splash_screen(self):
        print("[STATE] Showing splash screen")
        show_text_highlighted(["Doru.co Logo", "Welcome to Secure Wallet"], -1)
        time.sleep(3)

        try:
            with open("xdc_address.json", "r") as f:
                data = json.load(f)
                if "xdc_address" in data and "private_key" in data:
                    print("[INFO] Wallet found, skipping main menu")
                    self.generated_wallet = data
                    self.custom_network = load_custom_network()
                    self.current_state = MenuState.HOME_SCREEN
                    self.update_home_display()
                    return
        except (FileNotFoundError, json.JSONDecodeError):
            print("[INFO] No wallet file found, continue to Main Menu")

        self.custom_network = load_custom_network()

        self.current_state = MenuState.MAIN
        self.update_display()
    def handle_button_press(self, button):
        print(f"[INPUT] Button pressed: {button}, Current State: {self.current_state}")

        # --- Special case for typing during VERIFY_SEED ---
        if self.current_state == MenuState.VERIFY_SEED:
            if self.verification_successful:
                self.save_wallet_to_file()
                # ✅ Verification complete, go to Home Screen
                self.current_state = MenuState.HOME_SCREEN
                self.selected_option = 0
                self.update_home_display()
                return

            # During verification typing
            if button in ["UP", "ENTER"]:
                print("[DEBUG] Ignored UP/ENTER during verification typing")
                return
            if button == "DOWN":
                button = "C"  # Treat DOWN as Delete during typing

            handle_typing_input(self, button)  # Pass all typing buttons into typing handler
            return
        # ---------------------------------------------------

        # --- Normal behavior for other states ---
        if button in ["UP", "DOWN"]:
            self.handle_up_down(button)
        elif button == "ENTER":
            self.handle_enter()
        else:
            if self.current_state == MenuState.SEND_TRANSACTION_INPUT:
                self.handle_send_transaction_input(button)

    def handle_up_down(self, button):
        if self.current_state == MenuState.HOME_SCREEN:
            if button == "UP":
                self.selected_option = (self.selected_option - 1) % len(self.home_screen_options)
            elif button == "DOWN":
                self.selected_option = (self.selected_option + 1) % len(self.home_screen_options)
            self.update_home_display()

        elif self.current_state == MenuState.SELECT_COIN:
            if button == "UP":
                self.selected_option = (self.selected_option - 1) % len(self.coin_options)
            elif button == "DOWN":
                self.selected_option = (self.selected_option + 1) % len(self.coin_options)
            self.update_coin_selection_display()

        elif self.current_state == MenuState.CONFIRM_DELETE:
            self.selected_option = (self.selected_option + 1) % 2
            self.update_confirm_delete_display()

        elif self.current_state in [MenuState.MAIN, MenuState.CREATE_WALLET, MenuState.RESTORE_WALLET]:
            if button == "UP":
                self.selected_option = (self.selected_option - 1) % self.get_menu_length()
            elif button == "DOWN":
                self.selected_option = (self.selected_option + 1) % self.get_menu_length()
            self.update_display()

        elif self.current_state == MenuState.DISPLAY_SEED:
            if button == "UP":
                self.seed_screen_index = max(0, self.seed_screen_index - 1)
            elif button == "DOWN":
                total_screens = (len(self.generated_seed_phrase) + 2) // 3
                self.seed_screen_index = min(total_screens - 1, self.seed_screen_index + 1)
            self.update_display_seed()
    def handle_enter(self):
        if self.current_state == MenuState.HOME_SCREEN:
            self.execute_home_option()

        elif self.current_state == MenuState.SELECT_COIN:
            self.selected_coin = self.coin_options[self.selected_option]
            print(f"[INFO] Selected Coin: {self.selected_coin}")
            self.current_state = MenuState.SEND_TRANSACTION_INPUT
            self.tx_input_field = "receiver"
            self.tx_receiver = ""
            self.tx_amount = ""
            self.tx_nonce = ""
            self.update_transaction_input_display()

        elif self.current_state == MenuState.CONFIRM_DELETE:
            if self.selected_option == 0:  # YES
                self.delete_wallet()
            else:  # NO
                self.current_state = MenuState.HOME_SCREEN
                self.selected_option = 0
                self.update_home_display()

        elif self.current_state in [MenuState.MAIN, MenuState.CREATE_WALLET, MenuState.RESTORE_WALLET]:
            self.execute_selected_option()
            self.update_display()

        elif self.current_state == MenuState.DISPLAY_SEED:
            prepare_seed_verification(self)
            self.current_state = MenuState.VERIFY_SEED
            prompt_for_current_word(self)

        elif self.current_state == MenuState.SEND_TRANSACTION_INPUT:
            self.handle_send_transaction_input("ENTER")
    def execute_selected_option(self):
        if self.current_state == MenuState.MAIN:
            if self.selected_option == 0:  # Create Wallet
                self.current_state = MenuState.CREATE_WALLET
                self.selected_option = 0
            elif self.selected_option == 1:  # Restore Wallet
                self.current_state = MenuState.RESTORE_WALLET
                self.selected_option = 0

        elif self.current_state == MenuState.CREATE_WALLET:
            if self.selected_option == 0:  # 12 words
                self.generated_wallet = generate_wallet(12)
                self.generated_seed_phrase = self.generated_wallet["seed_phrase"]
                self.current_state = MenuState.DISPLAY_SEED
                self.seed_screen_index = 0
            elif self.selected_option == 1:  # 24 words
                self.generated_wallet = generate_wallet(24)
                self.generated_seed_phrase = self.generated_wallet["seed_phrase"]
                self.current_state = MenuState.DISPLAY_SEED
                self.seed_screen_index = 0
            elif self.selected_option == 2:  # Back
                self.current_state = MenuState.MAIN
                self.selected_option = 0

        elif self.current_state == MenuState.RESTORE_WALLET:
            if self.selected_option == 0:  # 12 words restore
                regenerate_wallet(12)
                self.current_state = MenuState.HOME_SCREEN
                self.selected_option = 0
            elif self.selected_option == 1:  # 24 words restore
                regenerate_wallet(24)
                self.current_state = MenuState.HOME_SCREEN
                self.selected_option = 0
            elif self.selected_option == 2:  # Back
                self.current_state = MenuState.MAIN
                self.selected_option = 0
    def execute_home_option(self):
        option = self.home_screen_options[self.selected_option]
        print(f"[ACTION] Selected Home Option: {option}")

        if option == "Back":
            self.go_back_to_main()
        elif option == "Send Transaction":
            self.current_state = MenuState.SELECT_COIN
            self.selected_option = 0
            self.update_coin_selection_display()
        elif option == "Receive Transaction":
            self.display_receive_qr()
        elif option == "Add Custom Network":
            add_custom_network_interactively(self)
        elif option == "Delete My Account":
            self.current_state = MenuState.CONFIRM_DELETE
            self.selected_option = 0
            self.update_confirm_delete_display()
        else:
            show_text_highlighted(["Selected:", option], -1)
            time.sleep(2)
            self.update_home_display()
    def delete_wallet(self):
        try:
            if os.path.exists("xdc_address.json"):
                os.remove("xdc_address.json")
                print("[INFO] Wallet deleted")
            if os.path.exists("custom_network.json"):
                os.remove("custom_network.json")
                print("[INFO] Custom network deleted")
        except Exception as e:
            print(f"[ERROR] Delete failed: {e}")

        self.generated_wallet = {}
        self.generated_seed_phrase = []
        self.entered_seed_phrase = []
        self.custom_network = None

        show_text_highlighted(["Account Deleted", "Returning to Main"], -1)
        time.sleep(2)
        self.current_state = MenuState.MAIN
        self.selected_option = 0
        self.update_display()

    def update_home_display(self):
        start = (self.selected_option // 3) * 3
        end = min(start + 3, len(self.home_screen_options))
        display_lines = [self.home_screen_options[i] for i in range(start, end)]
        while len(display_lines) < 3:
            display_lines.append("")
        show_text_highlighted(display_lines, self.selected_option % 3)
        self.current_state = MenuState.HOME_SCREEN

    def update_display(self):
        if self.current_state == MenuState.MAIN:
            show_text_highlighted(self.main_menu, self.selected_option)
        elif self.current_state == MenuState.CREATE_WALLET:
            show_text_highlighted(self.wallet_menu, self.selected_option)
        elif self.current_state == MenuState.RESTORE_WALLET:
            show_text_highlighted(self.restore_menu, self.selected_option)

    def update_coin_selection_display(self):
        self.coin_options = ["XDC", "Ethereum"]
        if self.custom_network:
            for network in self.custom_network:
                self.coin_options.append(network["name"])
        show_text_highlighted(self.coin_options, self.selected_option)

    def update_confirm_delete_display(self):
        options = ["Yes", "No"]
        display_lines = ["Confirm Delete?"] + ["> " + options[i] if i == self.selected_option else options[i] for i in range(2)]
        while len(display_lines) < 3:
            display_lines.append("")
        show_text_highlighted(display_lines, -1)
    def update_display_seed(self):
        start = self.seed_screen_index * 3
        end = min(start + 3, len(self.generated_seed_phrase))
        display_lines = [f"{i+1}. {self.generated_seed_phrase[i]}" for i in range(start, end)]
        while len(display_lines) < 3:
            display_lines.append("")
        show_text_highlighted(display_lines, -1)

    def display_receive_qr(self):
        address = self.get_sender_address_from_wallet()
        qr = qrcode.QRCode(box_size=2, border=1)
        qr.add_data(address)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        show_qr_on_display(img)
        time.sleep(5)
        self.update_home_display()

    def get_sender_address_from_wallet(self):
        try:
            with open("xdc_address.json", "r") as f:
                return json.load(f).get("xdc_address", "")
        except Exception:
            return ""

    def save_wallet_to_file(self):
        print("[INFO] Saving wallet to file")
        try:
            address_with_0x = self.generated_wallet.get("xdc_address", "")
            private_key = self.generated_wallet.get("private_key", "")
            if address_with_0x and private_key:
                with open("xdc_address.json", "w") as f:
                    json.dump({
                        "xdc_address": address_with_0x,
                        "private_key": private_key
                    }, f, indent=4)
                print("[INFO] Wallet saved successfully")
        except Exception as e:
            print(f"[ERROR] Failed to save wallet: {e}")
    def handle_send_transaction_input(self, button):
        if button == "ENTER":
            if self.tx_input_field == "receiver":
                self.tx_input_field = "amount"
            elif self.tx_input_field == "amount":
                self.tx_input_field = "nonce"
            elif self.tx_input_field == "nonce":
                print("[INFO] Attempting transaction creation")

                chain_id = 50  # Default XDC

                if self.selected_coin == "Ethereum":
                    chain_id = 11155111  # your custom setting
                elif self.custom_network:
                    for network in self.custom_network:
                        if self.selected_coin == network["name"]:
                            chain_id = network["chain_id"]
                            break

                success = generate_offline_transaction(
                    self.get_sender_address_from_wallet(),
                    self.tx_receiver,
                    self.tx_amount,
                    self.tx_nonce,
                    chain_id,
                    self.selected_coin
                )

                if success:
                    private_key = self.generated_wallet.get("private_key")
                    if private_key:
                        sign_transaction(private_key)
                    self.go_back_to_main()
                else:
                    show_text_highlighted(["Transaction Failed", "Check Inputs"], -1)
                    time.sleep(2)
                    self.go_back_to_main()

            self.update_transaction_input_display()

        elif button == "BACKSPACE":
            if self.tx_input_field == "receiver" and len(self.tx_receiver) > 0:
                self.tx_receiver = self.tx_receiver[:-1]
            elif self.tx_input_field == "amount" and len(self.tx_amount) > 0:
                self.tx_amount = self.tx_amount[:-1]
            elif self.tx_input_field == "nonce" and len(self.tx_nonce) > 0:
                self.tx_nonce = self.tx_nonce[:-1]

        elif button in ["D", "#"] and self.tx_input_field == "receiver":
            self.receive_address_via_qr()

        elif button == "*" and self.tx_input_field == "amount":
            if "." not in self.tx_amount:
                self.tx_amount += "."

        elif button.isdigit():
            if self.tx_input_field == "receiver":
                self.tx_receiver += button
            elif self.tx_input_field == "amount":
                self.tx_amount += button
            elif self.tx_input_field == "nonce":
                self.tx_nonce += button

        self.update_transaction_input_display()

    def update_transaction_input_display(self):
        if self.tx_input_field == "receiver":
            show_text_highlighted(["Receiver:", self.tx_receiver[-21:], "ENTER=Next | D=Scan"], -1)
        elif self.tx_input_field == "amount":
            show_text_highlighted(["Amount:", self.tx_amount, "*=dot | ENTER=Next"], -1)
        elif self.tx_input_field == "nonce":
            show_text_highlighted(["Nonce:", self.tx_nonce, "ENTER=Send"], -1)

    def receive_address_via_qr(self):
        scanned = scan_qr_code()
        if scanned:
            self.tx_receiver = scanned
            self.tx_input_field = "amount"
            self.update_transaction_input_display()

    def go_back_to_main(self):
        print("[INFO] Going back to Home screen")
        self.current_state = MenuState.HOME_SCREEN
        self.selected_option = 0
        self.generated_seed_phrase = []
        self.tx_input_field = ""
        self.tx_receiver = ""
        self.tx_amount = ""
        self.tx_nonce = ""
        self.update_home_display()

    def get_menu_length(self):
        if self.current_state in [MenuState.MAIN, MenuState.CREATE_WALLET, MenuState.RESTORE_WALLET]:
            return 3
        return 1
if __name__ == "__main__":
    try:
        setup_or_verify_pin() 
        wallet_ui = WalletUI()
        wallet_ui.show_splash_screen()
        poll_keypad(wallet_ui.handle_button_press)
    except KeyboardInterrupt:
        print("[EXIT] Exit by user")
