import cbor2
import qrcode
import base64
from mnemonic import Mnemonic
from bip32utils import BIP32Key
import binascii

def generate_ur_crypto_hdkey(word_count=12):
    """Generates a UR:CRYPTO-HDKEY QR code PNG for MetaMask-compatible wallet import."""

    # ✅ Step 1: Generate BIP39 Seed Phrase
    mnemo = Mnemonic("english")
    strength = 128 if word_count == 12 else 256  
    seed_phrase = mnemo.generate(strength=strength)

    # ✅ Step 2: Convert Mnemonic to a 512-bit BIP32 Seed
    seed = mnemo.to_seed(seed_phrase, passphrase="")

    # ✅ Step 3: Generate Master BIP32 Key
    master_key = BIP32Key.fromEntropy(seed)

    # ✅ Use Hardened Offset Instead of `BIP32Key.HARDEN`
    HARDENED_OFFSET = 0x80000000  

    # ✅ Step 4: Derive Ethereum HD Path (m/44'/60'/0'/0/0)
    purpose = master_key.ChildKey(44 + HARDENED_OFFSET)
    coin_type = purpose.ChildKey(60 + HARDENED_OFFSET)
    account = coin_type.ChildKey(0 + HARDENED_OFFSET)
    change = account.ChildKey(0)  
    address_index = change.ChildKey(0)

    # ✅ Extract Extended Public Key (xpub)
    xpub = address_index.ExtendedKey(private=False)

    # ✅ Format MetaMask `UR:CRYPTO-HDKEY`
    hdkey_data = {
        "crypto-hdkey": xpub  # The extended public key
    }

    # ✅ Encode in CBOR
    cbor_data = cbor2.dumps(hdkey_data)

    # ✅ Convert to Base64 (for UR encoding)
    base64_data = base64.b64encode(cbor_data).decode()

    # ✅ Generate UR:CRYPTO-HDKEY String
    ur_string = f"UR:CRYPTO-HDKEY/{base64_data}"

    print(f"\n✅ UR:CRYPTO-HDKEY Data (Copy & Paste into MetaMask):\n{ur_string}")

    # ✅ Generate QR Code for MetaMask
    qr = qrcode.QRCode(box_size=5, border=2)
    qr.add_data(ur_string)
    qr.make(fit=True)

    qr_image = qr.make_image(fill="black", back_color="white").convert("1")

    # ✅ Save QR Code as PNG
    qr_image_path = "metamask_hdkey_qr.png"
    qr_image.save(qr_image_path)
    print(f"\n✅ QR Code saved: {qr_image_path}")

    # ✅ Display QR Code
    qr_image.show()

    return seed_phrase, ur_string


if __name__ == "__main__":
    seed, ur_qr = generate_ur_crypto_hdkey(12)
    print("\n🔹 Your BIP39 Seed Phrase:")
    print(" ".join(seed))
