"""
Zer0n-Bench: Blockchain Logging Script
Logs vulnerability hashes to Avalanche Fuji C-Chain for provenance integrity.

Usage:
    1. Get test AVAX from faucet: https://faucet.avax.network/
    2. Set your PRIVATE_KEY environment variable
    3. Run: python log_to_blockchain.py
"""

from web3 import Web3
import csv
import time
import os

# ==========================================
# CONFIGURATION
# ==========================================
RPC_URL = "https://api.avax-test.network/ext/bc/C/rpc"
CONTRACT_ADDRESS = "0x9603145DFEEA4c3292186457BA2ab9b9562BA32c"
CSV_PATH = "blockchain/blockchain_proofs.csv"

# Contract ABI (minimal - just logVulnerabilityHash function)
ABI = [
    {
        "inputs": [{"internalType": "bytes32", "name": "_hash", "type": "bytes32"}],
        "name": "logVulnerabilityHash",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]


def main():
    """Main entry point for blockchain logging."""
    # Check for private key
    PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
    if not PRIVATE_KEY:
        print("ERROR: Please set PRIVATE_KEY environment variable")
        print("  Linux/Mac: export PRIVATE_KEY='your_key_here'")
        print("  Windows:   set PRIVATE_KEY=your_key_here")
        return

    # Connect to Avalanche Fuji
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("ERROR: Cannot connect to Avalanche Fuji. Check your internet.")
        return

    account = w3.eth.account.from_key(PRIVATE_KEY)
    wallet = account.address
    balance = w3.from_wei(w3.eth.get_balance(wallet), 'ether')
    print(f"Connected! Wallet: {wallet}")
    print(f"Balance: {balance} AVAX")

    if balance == 0:
        print("ERROR: Your wallet has 0 AVAX. Get test AVAX from: https://faucet.avax.network/")
        return

    # Load CSV
    with open(CSV_PATH, 'r') as f:
        rows = list(csv.DictReader(f))

    # Check for empty CSV
    if not rows:
        print("ERROR: blockchain_proofs.csv is empty.")
        return

    # Ensure new columns are in fieldnames
    fieldnames = list(rows[0].keys())
    for col in ['avalanche_tx_id', 'block_number', 'timestamp']:
        if col not in fieldnames:
            fieldnames.append(col)

    # Setup contract
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

    print(f"\nLogging {len(rows)} entries to Zer0nLog contract...")
    print(f"Contract: {CONTRACT_ADDRESS}")
    print(f"Verify at: https://testnet.snowtrace.io/address/{CONTRACT_ADDRESS}")
    print("=" * 50)

    for i, row in enumerate(rows):
        raw_hash = row['sha256_hash'].replace("0x", "")
        hash_bytes = bytes.fromhex(raw_hash)

        try:
            tx = contract.functions.logVulnerabilityHash(hash_bytes).build_transaction({
                'from': wallet,
                'nonce': w3.eth.get_transaction_count(wallet),
                'gas': 100000,
                'gasPrice': w3.eth.gas_price,
                'chainId': 43113  # Fuji Chain ID
            })
            signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            row['avalanche_tx_id'] = tx_hash.hex()
            row['block_number'] = receipt.blockNumber
            row['timestamp'] = int(time.time())

            if (i + 1) % 100 == 0:
                print(f"  [{i+1}/{len(rows)}] OK")

            time.sleep(0.5)  # Rate limiting

        except Exception as e:
            print(f"  [{i+1}/{len(rows)}] FAILED: {e}")

    # Save updated CSV with all columns
    with open(CSV_PATH, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDONE! All hashes logged to blockchain.")


if __name__ == "__main__":
    main()
