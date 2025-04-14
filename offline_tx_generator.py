import json
import time
from display import show_text_highlighted

def generate_offline_transaction(sender_address, receiver_address, amount_eth, nonce_input):
    try:
        # Validate receiver address
        if not receiver_address.startswith("0x") or len(receiver_address) != 42:
            raise ValueError("Receiver address format invalid")

        # Convert ETH to wei manually
        value = int(float(amount_eth) * 1e18)
        nonce = int(nonce_input)  # <-- updated here

    except Exception as e:
        show_text_highlighted(["\u274C Invalid TX Input", str(e)], -1)
        time.sleep(2)
        return False

    # Sepolia network constants
    gas = 21000
    gas_price = 12500000000  # 12.5 Gwei
    chain_id = 11155111

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
            f"Value: {amount_eth} ETH"
        ]
        show_text_highlighted(preview, -1)
        time.sleep(3)
        return True

    except Exception as e:
        show_text_highlighted(["❌ Save Failed", str(e)], -1)
        time.sleep(2)
        return False
