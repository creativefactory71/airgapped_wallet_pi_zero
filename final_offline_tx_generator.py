import json
import time
from display import show_text_highlighted

# Final Offline Transaction Generator

def generate_offline_transaction(sender_address, receiver_address, amount_eth, nonce_input, chain_id, coin_name="XDC"):
    try:
        # Validate receiver address
        if not receiver_address.startswith("0x") or len(receiver_address) != 42:
            raise ValueError("Receiver address format invalid")

        # Convert amount to wei manually
        value = int(float(amount_eth) * 1e18)
        nonce = int(nonce_input)

    except Exception as e:
        show_text_highlighted(["\u274C Invalid TX Input", str(e)], -1)
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
        with open("unsigned_tx.json", "w") as f:
            json.dump(tx, f)

        print("\n\U0001F512 Offline Transaction Preview:")
        print(f"Nonce     : {tx['nonce']}")
        print(f"To        : {tx['to']}")
        print(f"Value     : {tx['value']} wei")
        print(f"Gas       : {tx['gas']}")
        print(f"Gas Price : {tx['gasPrice']} wei")
        print(f"Chain ID  : {tx['chainId']}")
        print(f"Data      : {tx['data']}")

        preview = [
            "TX Saved \u2705",
            f"To: {receiver_address[:10]}...",
            f"Value: {amount_eth} {coin_name.upper()}"
        ]
        show_text_highlighted(preview, -1)
        time.sleep(3)
        return True

    except Exception as e:
        show_text_highlighted(["\u274C Save Failed", str(e)], -1)
        time.sleep(2)
        return False
