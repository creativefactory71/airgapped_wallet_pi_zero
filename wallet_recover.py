import binascii
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins

def recover_wallet(mnemonic):
    """Restores wallet details from a mnemonic phrase."""
    if not isinstance(mnemonic, str) or len(mnemonic.split()) not in [12, 24]:
        raise ValueError("Invalid mnemonic phrase. Please enter 12 or 24 words.")

    # Generate seed from mnemonic
    seed = Bip39SeedGenerator(mnemonic).Generate()

    # Derive master key for Ethereum (BIP44)
    master_key = Bip44.FromSeed(seed, Bip44Coins.ETHEREUM).DeriveDefaultPath()

    # Return wallet details
    return {
        "mnemonic": mnemonic,
        "seed_hex": binascii.hexlify(seed).decode(),
        "private_key": master_key.PrivateKey().Raw().ToHex(),
        "public_key": master_key.PublicKey().RawCompressed().ToHex(),
        "ethereum_address": master_key.PublicKey().ToAddress(),
    }
