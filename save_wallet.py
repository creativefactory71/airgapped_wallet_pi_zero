import json

def save_wallet_data(wallet_data, filename="wallet_data.json"):
    """Saves the wallet data to a JSON file and prints the data."""
    try:
        # Save data to a JSON file
        with open(filename, "w") as file:
            json.dump(wallet_data, file, indent=4)
        
        # Print the wallet data
        print("Wallet data saved successfully:")
        for key, value in wallet_data.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error saving wallet data: {e}")

# Example usage
if __name__ == "__main__":
    from wallet_generator import generate_wallet
    
    # Generate a new wallet
    wallet_details = generate_wallet()
    
    # Save and print the wallet details
    save_wallet_data(wallet_details)

