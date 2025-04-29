import json
import time
from bip_utils import (
    Bip39MnemonicGenerator, Bip39SeedGenerator, Bip39WordsNum,
    Bip32Slip10Secp256k1, EthAddrEncoder
)

def generate_wallet(word_count=12, coin="xdc", filename="xdc_address.json"):
    if word_count not in [12, 24]:
        raise ValueError("Word count must be 12 or 24.")
    if coin.lower() != "xdc":
        raise ValueError("Only 'xdc' is currently supported.")

    # Generate seed phrase and seed
    words_num = Bip39WordsNum.WORDS_NUM_12 if word_count == 12 else Bip39WordsNum.WORDS_NUM_24
    mnemonic = Bip39MnemonicGenerator().FromWordsNumber(words_num)
    seed = Bip39SeedGenerator(mnemonic).Generate()
    bip32 = Bip32Slip10Secp256k1.FromSeed(seed)
    xdc_key = bip32.DerivePath("m/44'/550'/0'/0/0")

    # Generate address and private key
    raw_address = EthAddrEncoder.EncodeKey(xdc_key.PublicKey().RawUncompressed().ToBytes()).replace("0x", "")
    address_with_0x = "0x" + raw_address
    private_key = xdc_key.PrivateKey().Raw().ToHex()

    # Display wallet details
    print("\n🔐 === Wallet Created ===")
    print(f"🧠 Seed Phrase       : {mnemonic.ToStr().split()}")
    print(f"🔹 Seed Hex          : {seed.hex()}")
    print(f"🔑 Private Key       : {private_key}")
    print(f"🏠 XDC Address       : {address_with_0x}\n")

    # Save to file
    """
    with open(filename, "w") as f:
        json.dump({
            "xdc_address": address_with_0x,
            "private_key": private_key
        }, f, indent=4)
    """
    return {
        "seed_phrase": mnemonic.ToStr().split(),
        "seed_hex": seed.hex(),
        "private_key": private_key,
        "public_key_compressed": xdc_key.PublicKey().RawCompressed().ToHex(),
        "xdc_address": address_with_0x,
    }