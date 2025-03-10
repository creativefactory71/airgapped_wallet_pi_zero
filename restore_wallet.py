from mnemonic import Mnemonic
import bip32utils
import binascii
from eth_keys import keys
from eth_utils import to_checksum_address, keccak

def regenerate_wallet(seed_phrase):
    """
    Regenerates an Ethereum wallet from a given BIP39 seed phrase.
    Supports both 12-word (128-bit) and 24-word (256-bit) phrases.
    """
    
    # Ensure the seed phrase is a valid list of words
    if not isinstance(seed_phrase, list) or len(seed_phrase) not in [12, 24]:
        raise ValueError("Seed phrase must be a list of 12 or 24 words.")
    
    # Convert the seed phrase to a 512-bit Seed
    mnemo = Mnemonic("english")
    passphrase = ""  # Optional security passphrase
    seed = mnemo.to_seed(" ".join(seed_phrase), passphrase)

    # Derive Master Private Key using BIP32
    master_key = bip32utils.BIP32Key.fromEntropy(seed)

    # BIP44 Path for Ethereum: m/44'/60'/0'/0/0
    purpose = master_key.ChildKey(44 + bip32utils.BIP32_HARDEN)
    coin_type = purpose.ChildKey(60 + bip32utils.BIP32_HARDEN)  # 60 for Ethereum
    account = coin_type.ChildKey(0 + bip32utils.BIP32_HARDEN)  # First account
    change = account.ChildKey(0)  # External chain (0)
    address_index = change.ChildKey(0)  # First Ethereum address

    # Extract the Private Key
    eth_private_key = binascii.hexlify(address_index.PrivateKey()).decode()

    # Generate Ethereum Public Address
    priv_key_bytes = binascii.unhexlify(eth_private_key)
    eth_private_key_obj = keys.PrivateKey(priv_key_bytes)
    
    eth_public_key = eth_private_key_obj.public_key
    eth_address = keccak(eth_public_key.to_bytes())[12:]  # Last 20 bytes of Keccak-256 hash
    eth_checksum_address = to_checksum_address("0x" + eth_address.hex())

    # Print wallet details
    print("\n✅ Wallet Successfully Regenerated:")
    print(f"🔹 Seed Hex: {seed.hex()}")
    print(f"🔹 Private Key: {eth_private_key}")
    print(f"🔹 Public Key: {eth_public_key.to_bytes().hex()}")
    print(f"🔹 ETH Address: {eth_checksum_address}\n")

    # Return wallet details
    return {
        "seed_phrase": seed_phrase,
        "seed_hex": seed.hex(),
        "private_key": eth_private_key,
        "public_key": eth_public_key.to_bytes().hex(),
        "eth_address": eth_checksum_address
    }
