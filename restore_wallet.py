import json
from bip_utils import Bip39SeedGenerator, Bip32Slip10Secp256k1, EthAddrEncoder

def regenerate_wallet(seed_phrase, coin="xdc"):
    if not isinstance(seed_phrase, list) or len(seed_phrase) not in [12, 24]:
        raise ValueError("Seed phrase must be a list of 12 or 24 words.")
    if coin.lower() != "xdc":
        raise ValueError("Only 'xdc' is supported.")

    mnemonic_str = " ".join(seed_phrase)
    seed = Bip39SeedGenerator(mnemonic_str).Generate()
    bip32 = Bip32Slip10Secp256k1.FromSeed(seed)
    xdc_key = bip32.DerivePath("m/44'/550'/0'/0/0")

    private_key = xdc_key.PrivateKey().Raw().ToHex()
    public_key = xdc_key.PublicKey().RawCompressed().ToHex()
    raw_address = EthAddrEncoder.EncodeKey(xdc_key.PublicKey().RawUncompressed().ToBytes()).replace("0x", "")
    address_with_0x = "0x" + raw_address

    print("\n🔁 === Wallet Regenerated ===")
    print(f"🔑 Private Key       : {private_key}")
    print(f"🔓 Public Key (comp) : {public_key}")
    print(f"🏠 XDC Address (0x)  : {address_with_0x}\n")

    # ✅ Save both address and private key to JSON
    with open("xdc_address.json", "w") as f:
        json.dump({
            "xdc_address": address_with_0x,
            "private_key": private_key
        }, f, indent=4)

    return {
        "seed_phrase": seed_phrase,
        "seed_hex": seed.hex(),
        "private_key": private_key,
        "public_key_compressed": public_key,
        "xdc_address": address_with_0x,
    }
