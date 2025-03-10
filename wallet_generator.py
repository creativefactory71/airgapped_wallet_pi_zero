from mnemonic import Mnemonic
import bip32utils
import binascii
from eth_keys import keys
from eth_utils import to_checksum_address, keccak

def generate_wallet(word_count=12):
    """Generates a BIP39 seed phrase and derives wallet details."""
    if word_count not in [12, 24]:
        raise ValueError("Word count must be 12 or 24.")

    # Step 1: Generate a BIP39 Seed Phrase
    mnemo = Mnemonic("english")
    strength = 128 if word_count == 12 else 256  # 128-bit for 12 words, 256-bit for 24 words
    seed_phrase = mnemo.generate(strength=strength)
    
    # Step 2: Convert Mnemonic to a 512-bit Seed
    passphrase = ""  # Optional for extra security
    seed = mnemo.to_seed(seed_phrase, passphrase)
    
    # Step 3: Derive the Master Private Key using BIP32
    master_key = bip32utils.BIP32Key.fromEntropy(seed)

    # Step 4: Derive Child Keys (BIP44 for Ethereum)
    purpose = master_key.ChildKey(44 + bip32utils.BIP32_HARDEN)
    coin_type = purpose.ChildKey(60 + bip32utils.BIP32_HARDEN)  # 60 for Ethereum
    account = coin_type.ChildKey(0 + bip32utils.BIP32_HARDEN)  # First account
    change = account.ChildKey(0)  # External chain (0)
    address_index = change.ChildKey(0)  # First Ethereum address

    # Step 5: Extract the Private Key for Ethereum
    eth_private_key = binascii.hexlify(address_index.PrivateKey()).decode()

    # Step 6: Generate Ethereum Public Address
    priv_key_bytes = binascii.unhexlify(eth_private_key)
    eth_private_key_obj = keys.PrivateKey(priv_key_bytes)
    
    eth_public_key = eth_private_key_obj.public_key
    eth_address = keccak(eth_public_key.to_bytes())[12:]  # Last 20 bytes of Keccak-256 hash
    eth_checksum_address = to_checksum_address("0x" + eth_address.hex())
    print(f"🔹 Seed seed_phrase : {seed_phrase.split()}")
    print(f"🔹 Seed Hex: {seed.hex()}")
    print(f"🔹 Private Key: {eth_private_key}")
    print(f"🔹 Public Key: {eth_public_key.to_bytes().hex()}")
    print(f"🔹 ETH Address: {eth_checksum_address}\n")


    # Return wallet details
    return {
        "seed_phrase": seed_phrase.split(),  # Split into individual words
        "seed_hex": seed.hex(),
        "private_key": eth_private_key,
        "public_key": eth_public_key.to_bytes().hex(),
        "eth_address": eth_checksum_address
    }
