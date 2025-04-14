from bip_utils import (
    Bip39MnemonicGenerator, Bip39SeedGenerator, Bip39WordsNum,
    Bip32Slip10Secp256k1, EthAddrEncoder
)

def generate_wallet(word_count=12, coin="xdc"):
    if word_count not in [12, 24]:
        raise ValueError("Word count must be 12 or 24.")
    if coin.lower() != "xdc":
        raise ValueError("Only 'xdc' is currently supported in this version.")

    # ✅ Generate mnemonic
    words_num = Bip39WordsNum.WORDS_NUM_12 if word_count == 12 else Bip39WordsNum.WORDS_NUM_24
    mnemonic = Bip39MnemonicGenerator().FromWordsNumber(words_num)

    # ✅ Generate seed
    seed = Bip39SeedGenerator(mnemonic).Generate()

    # ✅ Derive XDC key using BIP32 path m/44'/550'/0'/0/0
    bip32 = Bip32Slip10Secp256k1.FromSeed(seed)
    xdc_key = bip32.DerivePath("m/44'/550'/0'/0/0")

    # ✅ Extract keys
    private_key = xdc_key.PrivateKey().Raw().ToHex()
    public_key = xdc_key.PublicKey().RawCompressed().ToHex()
    raw_address = EthAddrEncoder.EncodeKey(xdc_key.PublicKey().RawUncompressed().ToBytes()).replace("0x", "")
    address_with_0x = "0x" + raw_address  # 👈 Add 0x prefix only

    # ✅ Print wallet details
    print("\n🔐 === Wallet Details ===")
    print(f"🧠 Seed Phrase       : {mnemonic.ToStr().split()}")
    print(f"🔹 Seed Hex          : {seed.hex()}")
    print(f"🔑 Private Key       : {private_key}")
    print(f"🔓 Public Key (comp) : {public_key}")
    print(f"🏠 XDC Address (0x)  : {address_with_0x}\n")  # 👈 Address with only 0x prefix

    return {
        "seed_phrase": mnemonic.ToStr().split(),
        "seed_hex": seed.hex(),
        "private_key": private_key,
        "public_key_compressed": public_key,
        "xdc_address": address_with_0x,
    }
