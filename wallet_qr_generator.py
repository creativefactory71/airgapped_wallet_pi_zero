import cbor2
import base64
from wallet_generator import generate_wallet

def get_wallet_qr_data():
    """Generates wallet and returns QR-compatible data."""
    wallet_data = generate_wallet()

    # Encode Wallet Data into CBOR
    cbor_encoded = cbor2.dumps(wallet_data)

    # Convert CBOR to Base64 (UR-like Encoding)
    ur_encoded = "ur:crypto-wallet/" + base64.urlsafe_b64encode(cbor_encoded).decode()

    return ur_encoded  # ✅ Return the encoded wallet data
