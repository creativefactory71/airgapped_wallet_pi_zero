import json
import os

CONFIG_FILE = "blockchain_config.json"

DEFAULT_NETWORKS = {
    "BTC": {
        "chain_id": 0,
        "rpc_url": "https://blockstream.info/api",
        "symbol": "BTC",
        "network_type": "UTXO"
    },
    "ETH": {
        "chain_id": 1,
        "rpc_url": "https://mainnet.infura.io/v3/YOUR_INFURA_API_KEY",
        "symbol": "ETH",
        "network_type": "EVM"
    },
    "XDC": {
        "chain_id": 50,
        "rpc_url": "https://rpc.xinfin.network",
        "symbol": "XDC",
        "network_type": "EVM"
    }
}

def load_blockchain_config():
    """Loads blockchain network configurations."""
    if not os.path.exists(CONFIG_FILE):
        save_blockchain_config(DEFAULT_NETWORKS)
    
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_blockchain_config(config):
    """Saves blockchain network configurations to a file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    print("✅ Blockchain configuration saved!")
