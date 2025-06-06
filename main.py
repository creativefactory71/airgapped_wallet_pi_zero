import time
import RPi.GPIO as GPIO
from display import show_text_highlighted
from button_handler import setup_buttons, poll_buttons
from wallet_generator import generate_wallet
from restore_wallet import regenerate_wallet  # Import restore wallet function
from wallet_qr_generator import get_wallet_qr_data
from qr_show import generate_qr_for_hdkey  # ✅ Import the QR display function


# === MENU STATES ENUM ===
class MenuState:
    SPLASH = 0
    MAIN = 1
    CREATE_WALLET = 2
    RESTORE_WALLET = 3
    ENTER_SEED = 4
    DISPLAY_SEED = 5
    CONFIRMATION = 6
    DISPLAY_RESTORED = 7
    HOME_SCREEN = 8  # ✅ Added Home Screen State

class WalletUI:
    def __init__(self):
        """Initialize menu system and GPIO buttons."""
        self.current_state = MenuState.SPLASH
        self.selected_option = 0
        self.generated_seed_phrase = []
        self.entered_seed_phrase = []  # Stores entered seed words
        self.seed_screen_index = 0  # Track which group of 3 words is shown

        # Define menus
        self.main_menu = ["Create Wallet", "Restore Wallet"]
        self.wallet_menu = ["12 words", "24 words", "Back"]
        self.restore_menu = ["12 words", "24 words", "Back"]
        self.confirm_menu = ["Yes", "No"]

        # ✅ Add Home Screen Menu Options
        self.home_screen_options = [
            "Sign Transaction",
            "Send Transaction",
            "Receive Transaction",
            "Add Custom Network",
            "Settings",
            "Device Info",
            "Back"
        ]
        self.home_screen_index = 0  # ✅ Track pagination for 3-line display

    def show_splash_screen(self):
        """Displays splash screen and transitions to the main menu."""
        show_text_highlighted(["Doru.co Logo", "Welcome to Secure Wallet"], -1)
        time.sleep(3)
        self.current_state = MenuState.MAIN
        self.update_display()

    def handle_button_press(self, button):
        """Handles user navigation input via button presses."""
        
        if self.current_state == MenuState.DISPLAY_SEED:
            if button == "UP":
                self.seed_screen_index = max(0, self.seed_screen_index - 1)
            elif button == "DOWN":
                total_screens = (len(self.generated_seed_phrase) + 2) // 3
                self.seed_screen_index = min(total_screens - 1, self.seed_screen_index + 1)
            elif button == "ENTER":
                if self.seed_screen_index == (len(self.generated_seed_phrase) + 2) // 3 - 1:
                    self.current_state = MenuState.CONFIRMATION
                    self.selected_option = 0
            self.update_display()

        elif self.current_state == MenuState.HOME_SCREEN:  # ✅ Home Screen Navigation
            if button == "UP":
                self.selected_option = (self.selected_option - 1) % len(self.home_screen_options)
            elif button == "DOWN":
                self.selected_option = (self.selected_option + 1) % len(self.home_screen_options)
            elif button == "ENTER":
                self.execute_home_option()
            self.update_home_display()

        else:
            if button == "UP":
                self.selected_option = (self.selected_option - 1) % self.get_menu_length()
            elif button == "DOWN":
                self.selected_option = (self.selected_option + 1) % self.get_menu_length()
            elif button == "ENTER":
                self.execute_selected_option()
            self.update_display()

    def execute_selected_option(self):
        """Executes the selected menu option."""
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
                self.generated_wallet = generate_wallet(seed_length)  # ✅ Store full wallet data
                self.generated_seed_phrase = self.generated_wallet["seed_phrase"]  # ✅ Extract only the seed phrase
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

        elif self.current_state == MenuState.CONFIRMATION:
            if self.selected_option == 0:  # ✅ If "Yes" is selected
                print("\n[INFO] Generating Wallet QR Code...")

                if hasattr(self, "generated_wallet") and "private_key" in self.generated_wallet:
                    private_key = self.generated_wallet["private_key"]
                    print(f"🔑 HD Private Key: {private_key}")  # ✅ Debugging: Print private key

                # ✅ Pass only the private key to QR generator
                    generate_qr_for_hdkey(private_key)
                else:
                    print("❌ Error: Wallet not generated or incorrect format!")

            # ✅ Redirect to Home Screen
                self.current_state = MenuState.HOME_SCREEN  
                self.update_home_display()

            elif self.selected_option == 1:  # If "No" is selected
                self.go_back_to_main()

    def enter_seed_words(self, word_count):
        """Allows the user to enter a seed phrase via keyboard."""
        print(f"\n[INFO] Enter your {word_count}-word seed phrase:")
        entered_seed = []
        for i in range(word_count):
            word = input(f"Word {i+1}: ").strip()
            entered_seed.append(word)

        # Validate and restore wallet
        self.entered_seed_phrase = entered_seed
        self.restore_wallet()

    def restore_wallet(self):
        """Calls the restore function and displays the wallet details."""
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

    def update_display_seed(self):
        """Displays 3 words of the seed phrase per screen."""
        start_index = self.seed_screen_index * 3
        end_index = min(start_index + 3, len(self.generated_seed_phrase))

        display_lines = [f"{i+1}. {self.generated_seed_phrase[i]}" for i in range(start_index, end_index)]
        while len(display_lines) < 3:
            display_lines.append("")

        show_text_highlighted(display_lines, -1)

    def get_menu_length(self):
        """Returns the length of the active menu to prevent out-of-range errors."""
        if self.current_state == MenuState.MAIN:
            return len(self.main_menu)
        elif self.current_state in [MenuState.CREATE_WALLET, MenuState.RESTORE_WALLET]:
            return len(self.wallet_menu)
        elif self.current_state == MenuState.CONFIRMATION:
            return len(self.confirm_menu)
        return 1

    def update_display(self):
        """Updates the UI based on the current state."""
        if self.current_state == MenuState.MAIN:
            show_text_highlighted(self.main_menu, self.selected_option)
        elif self.current_state == MenuState.CREATE_WALLET:
            show_text_highlighted(self.wallet_menu, self.selected_option)
        elif self.current_state == MenuState.RESTORE_WALLET:
            show_text_highlighted(self.restore_menu, self.selected_option)
        elif self.current_state == MenuState.DISPLAY_SEED:
            self.update_display_seed()
        elif self.current_state == MenuState.CONFIRMATION:
            show_text_highlighted(["Confirmed?", self.confirm_menu[0], self.confirm_menu[1]], self.selected_option + 1)
        elif self.current_state == MenuState.HOME_SCREEN:
            self.update_home_display()  # ✅ Ensure Home Screen is updated properly


    def update_home_display(self):
        """Displays 3 options at a time from the Home Screen menu."""
        start_index = (self.selected_option // 3) * 3
        end_index = min(start_index + 3, len(self.home_screen_options))

        display_lines = [self.home_screen_options[i] for i in range(start_index, end_index)]
    
    # Ensure 3 lines are always displayed
        while len(display_lines) < 3:
            display_lines.append("")

        show_text_highlighted(display_lines, self.selected_option % 3)

# === MAIN EXECUTION ===
if __name__ == "__main__":
    try:
        wallet_ui = WalletUI()
        setup_buttons()
        wallet_ui.show_splash_screen()
        poll_buttons(wallet_ui.handle_button_press)
    except KeyboardInterrupt:
        print("\n[DEBUG] Exiting...")
    finally:
        GPIO.cleanup()
