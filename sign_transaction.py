from web3 import Web3
import json
import time
import qrcode
from PIL import Image
from display import show_qr_on_display  # ✅ Use the new function

def sign_transaction(private_key):
    try:
        # Load the unsigned transaction
        with open("unsigned_tx.json", "r") as f:
            tx = json.load(f)

        # Sign the transaction
        signed = Web3().eth.account.sign_transaction(tx, private_key)
        signed_hex = signed.raw_transaction.hex()

        # Save to file
        with open("signed_tx.txt", "w") as f:
            f.write(signed_hex)

        print("\n✅ Signed transaction saved to signed_tx.txt")

        # ✅ Generate and display QR
        qr = qrcode.QRCode(box_size=2, border=1)
        qr.add_data(signed_hex)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("1")

        show_qr_on_display(qr_img)  # ✅ Show on your color display
        time.sleep(50)  # ⏳ Keep QR visible for 10 seconds

        return signed_hex

    except Exception as e:
        print(f"\n❌ Signing failed: {e}")
        return None
