from wallet_generator import generate_wallet
from wallet_ur_converter import convert_to_ur

# Step 1: Generate Wallet
wallet_data = generate_wallet(word_count=12)

# Step 2: Ask User for Confirmation
user_input = input("Do you want to convert the wallet to UR format? (yes/no): ")

if user_input.lower() == "yes":
    ur_data = convert_to_ur(wallet_data)
    print("\n🔹 UR Format:\n", ur_data)
else:
    print("\nWallet generation complete. No conversion applied.")
