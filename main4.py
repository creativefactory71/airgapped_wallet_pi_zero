import time
import json
from blockchain_config import load_blockchain_config
from display import show_text_highlighted
from button_handler import poll_keypad
from wallet_generator import generate_wallet
from restore_wallet import regenerate_wallet
from offline_tx_generator import generate_offline_transaction
from qr_scanner import scan_qr_code
from sign_transaction import sign_transaction

class MenuState:
    SPLASH = 0
    MAIN = 1
    CREATE_WALLET = 2
    RESTORE_WALLET = 3
    ENTER_SEED = 4
    DISPLAY_SEED = 5
    DISPLAY_RESTORED = 6
    HOME_SCREEN = 7
    SELECT_CRYPTO = 8
    SEND_TRANSACTION_INPUT = 9
    SEND_TRANSACTION_CONFIRM = 10

class WalletUI:
    def __init__(self):
        self.current_state = MenuState.SPLASH
        self.selected_option = 0
        self.generated_wallet = {}
        self.generated_seed_phrase = []
        self.entered_seed_phrase = []
        self.seed_screen_index = 0

        self.main_menu = ["Create Wallet", "Restore Wallet"]
        self.wallet_menu = ["12 words", "24 words", "Back"]
        self.restore_menu = ["12 words", "24 words", "Back"]

        self.home_screen_options = [
            "Sign Transaction",
            "Send Transaction",
            "Receive Transaction",
            "Add Custom Network",
            "Settings",
            "Device Info",
            "Back"
        ]

        self.tx_input_field = "receiver"
        self.tx_receiver = ""
        self.tx_amount = ""

    def show_splash_screen(self):
        show_text_highlighted(["Doru.co Logo", "Welcome to Secure Wallet"], -1)
        time.sleep(3)
        self.current_state = MenuState.MAIN
        self.update_display()

    def handle_button_press(self, button):
        if self.current_state == MenuState.DISPLAY_SEED:
            if button == "UP":
                self.seed_screen_index = max(0, self.seed_screen_index - 1)
            elif button == "DOWN":
                total_screens = (len(self.generated_seed_phrase) + 2) // 3
                self.seed_screen_index = min(total_screens - 1, self.seed_screen_index + 1)
            elif button == "ENTER":
                if self.seed_screen_index == (len(self.generated_seed_phrase) + 2) // 3 - 1:
                    self.current_state = MenuState.HOME_SCREEN
                    self.selected_option = 0
                    self.update_home_display()
            self.update_display()

        elif self.current_state == MenuState.HOME_SCREEN:
            if button == "UP":
                self.selected_option = (self.selected_option - 1) % len(self.home_screen_options)
            elif button == "DOWN":
                self.selected_option = (self.selected_option + 1) % len(self.home_screen_options)
            elif button == "ENTER":
                self.execute_home_option()
            self.update_home_display()

        elif self.current_state == MenuState.SEND_TRANSACTION_INPUT:
            if button == "ENTER":
                if self.tx_input_field == "receiver":
                    self.tx_input_field = "amount"
                elif self.tx_input_field == "amount":
                    success = generate_offline_transaction(
                        self.get_sender_address_from_wallet(),
                        self.tx_receiver,
                        self.tx_amount
                    )
                    if success:
                        private_key = self.generated_wallet.get("private_key")
                        if private_key:
                            sign_transaction(private_key)
                        self.go_back_to_main()
                    else:
                        self.tx_receiver = ""
                        self.tx_amount = ""
                        self.tx_input_field = "receiver"
                        self.update_transaction_input_display()
                    return
            elif button == "BACKSPACE":
                if self.tx_input_field == "receiver" and len(self.tx_receiver) > 0:
                    self.tx_receiver = self.tx_receiver[:-1]
                elif self.tx_input_field == "amount" and len(self.tx_amount) > 0:
                    self.tx_amount = self.tx_amount[:-1]
            elif button in ["D", "#"]:
                self.receive_address_via_qr()
            elif button == "*" and self.tx_input_field == "amount":
                if "." not in self.tx_amount:
                    self.tx_amount += "."
            elif button.isdigit():
                if self.tx_input_field == "receiver":
                    self.tx_receiver += button
                elif self.tx_input_field == "amount":
                    self.tx_amount += button
            self.update_transaction_input_display()

        else:
            if button == "UP":
                self.selected_option = (self.selected_option - 1) % self.get_menu_length()
            elif button == "DOWN":
                self.selected_option = (self.selected_option + 1) % self.get_menu_length()
            elif button == "ENTER":
                self.execute_selected_option()
            self.update_display()

    def receive_address_via_qr(self):
        scanned_address = scan_qr_code()
        if scanned_address:
            self.tx_receiver = scanned_address
            self.tx_input_field = "amount"
            self.update_transaction_input_display()

    def execute_selected_option(self):
        if self.current_state == MenuState.MAIN:
            if self.selected_option == 0:
                self.current_state = MenuState.CREATE_WALLET
            elif self.selected_option == 1:
                self.current_state = MenuState.RESTORE_WALLET
            self.selected_option = 0

        elif self.current_state == MenuState.CREATE_WALLET:
            if self.selected_option == 2:
                self.go_back_to_main()
            else:
                seed_length = 12 if self.selected_option == 0 else 24
                self.generated_wallet = generate_wallet(seed_length, "xdc")
                self.generated_seed_phrase = self.generated_wallet["seed_phrase"]
                self.seed_screen_index = 0
                self.current_state = MenuState.DISPLAY_SEED
                self.selected_option = 0

        elif self.current_state == MenuState.RESTORE_WALLET:
            if self.selected_option == 2:
                self.go_back_to_main()
            else:
                self.enter_seed_words(12 if self.selected_option == 0 else 24)

        elif self.current_state == MenuState.DISPLAY_RESTORED:
            self.current_state = MenuState.HOME_SCREEN
            self.selected_option = 0
            self.update_home_display()

    def enter_seed_words(self, word_count):
        print(f"\n[INFO] Enter your {word_count}-word seed phrase:")
        entered_seed = []
        for i in range(word_count):
            word = input(f"Word {i+1}: ").strip()
            entered_seed.append(word)

        self.entered_seed_phrase = entered_seed
        self.restore_wallet()

    def restore_wallet(self):
        try:
            restored_wallet = regenerate_wallet(self.entered_seed_phrase)
            display_lines = [
                "Wallet Restored!",
                f"ETH Address: {restored_wallet['eth_address'][:10]}...",
                "Press ENTER"
            ]
            self.current_state = MenuState.DISPLAY_RESTORED
            show_text_highlighted(display_lines, -1)
        except ValueError as e:
            print(f"\n[ERROR] {e}")
            show_text_highlighted(["Invalid Seed!", "Try Again"], -1)
            time.sleep(2)
            self.current_state = MenuState.RESTORE_WALLET
        self.selected_option = 0
        self.update_display()

    def execute_home_option(self):
        option = self.home_screen_options[self.selected_option]
        if option == "Back":
            self.go_back_to_main()
        elif option == "Send Transaction":
            self.current_state = MenuState.SEND_TRANSACTION_INPUT
            self.tx_input_field = "receiver"
            self.tx_receiver = ""
            self.tx_amount = ""
            self.update_transaction_input_display()
        elif option == "Receive Transaction":
            self.current_state = MenuState.SELECT_CRYPTO
            self.selected_option = 0
            self.update_crypto_display()
        else:
            show_text_highlighted(["Selected:", option], -1)
            time.sleep(2)
            self.update_home_display()

    def update_transaction_input_display(self):
        if self.tx_input_field == "receiver":
            show_text_highlighted(["To Address:", self.tx_receiver[-21:], "ENTER=Next | D=Scan"], -1)
        elif self.tx_input_field == "amount":
            show_text_highlighted(["Amount (ETH):", self.tx_amount, "* = dot"], -1)

    def get_sender_address_from_wallet(self):
        return self.generated_wallet.get("xdc_address", "0x0000000000000000000000000000000000000000")

    def get_menu_length(self):
        if self.current_state == MenuState.MAIN:
            return len(self.main_menu)
        elif self.current_state in [MenuState.CREATE_WALLET, MenuState.RESTORE_WALLET]:
            return len(self.wallet_menu)
        return 1

    def update_display(self):
        if self.current_state == MenuState.MAIN:
            show_text_highlighted(self.main_menu, self.selected_option)
        elif self.current_state == MenuState.CREATE_WALLET:
            show_text_highlighted(self.wallet_menu, self.selected_option)
        elif self.current_state == MenuState.RESTORE_WALLET:
            show_text_highlighted(self.restore_menu, self.selected_option)
        elif self.current_state == MenuState.DISPLAY_SEED:
            self.update_display_seed()
        elif self.current_state == MenuState.HOME_SCREEN:
            self.update_home_display()

    def update_display_seed(self):
        start_index = self.seed_screen_index * 3
        end_index = min(start_index + 3, len(self.generated_seed_phrase))
        display_lines = [f"{i+1}. {self.generated_seed_phrase[i]}" for i in range(start_index, end_index)]
        while len(display_lines) < 3:
            display_lines.append("")
        show_text_highlighted(display_lines, -1)

    def update_home_display(self):
        start_index = (self.selected_option // 3) * 3
        end_index = min(start_index + 3, len(self.home_screen_options))
        display_lines = [self.home_screen_options[i] for i in range(start_index, end_index)]
        while len(display_lines) < 3:
            display_lines.append("")
        show_text_highlighted(display_lines, self.selected_option % 3)

    def update_crypto_display(self):
        crypto_options = ["BTC", "ETH", "XDC"]
        show_text_highlighted(crypto_options, self.selected_option)

    def go_back_to_main(self):
        self.current_state = MenuState.HOME_SCREEN
        self.selected_option = 0
        self.generated_seed_phrase = []
        self.update_display()

if __name__ == "__main__":
    try:
        wallet_ui = WalletUI()
        wallet_ui.show_splash_screen()
        poll_keypad(wallet_ui.handle_button_press)
    except KeyboardInterrupt:
        print("\n[DEBUG] Exiting...")