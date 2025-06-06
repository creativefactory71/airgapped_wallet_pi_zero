import json
import time
import os  # ✅ Import os to delete file
from display import show_text_highlighted

# Mapping coin name to chain ID
CHAIN_IDS = {
    "XDC": 50,
    "ETHEREUM": 11155111
}

def generate_offline_transaction(sender_address, receiver_address, amount_eth, nonce_input, coin):
    try:
        # Validate receiver address
        if not receiver_address.startswith("0x") or len(receiver_address) != 42:
            raise ValueError("Receiver address format invalid")

        # Convert ETH to wei manually
        value = int(float(amount_eth) * 1e18)
        nonce = int(nonce_input)

        # Set chain ID from selected coin
        coin_upper = coin.upper()
        if coin_upper not in CHAIN_IDS:
            raise ValueError("Unsupported coin selected")
        chain_id = CHAIN_IDS[coin_upper]

    except Exception as e:
        show_text_highlighted(["❌ Invalid TX Input", str(e)], -1)
        time.sleep(2)
        return False

    # Transaction parameters
    gas = 21000
    gas_price = 12500000000  # 12.5 Gwei

    tx = {
        "nonce": nonce,
        "to": receiver_address,
        "value": value,
        "gas": gas,
        "gasPrice": gas_price,
        "chainId": chain_id,
        "data": "0x"
    }

    try:
        # ✅ Before saving, delete previous unsigned_tx.json if exists
        if os.path.exists("unsigned_tx.json"):
            os.remove("unsigned_tx.json")
            print("[INFO] Old unsigned_tx.json deleted")

        # Save new unsigned transaction
        with open("unsigned_tx.json", "w") as f:
            json.dump(tx, f)

        print("\n🔒 Offline Transaction Preview:")
        print(f"Nonce     : {tx['nonce']}")
        print(f"To        : {tx['to']}")
        print(f"Value     : {tx['value']} wei")
        print(f"Gas       : {tx['gas']}")
        print(f"Gas Price : {tx['gasPrice']} wei")
        print(f"Chain ID  : {tx['chainId']}")
        print(f"Data      : {tx['data']}")

        preview = [
            "TX Saved ✅",
            f"To: {receiver_address[:10]}...",
            f"Value: {amount_eth} {coin_upper}"
        ]
        show_text_highlighted(preview, -1)
        time.sleep(3)
        return True

    except Exception as e:
        show_text_highlighted(["❌ Save Failed", str(e)], -1)
        time.sleep(2)
        return False
