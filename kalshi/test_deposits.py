#!/usr/bin/env python3
"""
Test script to check if we can retrieve deposit history using git_clients.py
"""

import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from git_clients import KalshiHttpClient, Environment

# Load environment variables
load_dotenv()
env = Environment.PROD  # Use production environment
KEYID = os.getenv('DEMO_KEYID') if env == Environment.DEMO else os.getenv('PROD_KEYID')
KEYFILE = os.getenv('DEMO_KEYFILE') if env == Environment.DEMO else os.getenv('PROD_KEYFILE')

try:
    with open(KEYFILE, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )
except FileNotFoundError:
    raise FileNotFoundError(f"Private key file not found at {KEYFILE}")
except Exception as e:
    raise Exception(f"Error loading private key: {str(e)}")

# Initialize the HTTP client
client = KalshiHttpClient(
    key_id=KEYID,
    private_key=private_key,
    environment=env
)

def test_deposits():
    """Test retrieving deposit history."""
    print("=" * 60)
    print("TESTING DEPOSIT HISTORY RETRIEVAL")
    print("=" * 60)
    
    try:
        # Test balance first to confirm connection
        print("1. Testing balance...")
        balance = client.get_balance()
        print(f"   Balance: ${balance.get('balance', 0) / 100:.2f}")
        
        print("\n2. Testing account history...")
        history = client.get_account_history(limit=50)
        
        if 'history' in history:
            history_list = history['history']
            print(f"   Found {len(history_list)} account history records")
            
            # Filter for deposits
            deposits = [h for h in history_list if 'deposit' in h.get('type', '').lower()]
            print(f"   Found {len(deposits)} deposits")
            
            for i, deposit in enumerate(deposits[:5]):  # Show first 5
                amount = deposit.get('amount', 0)
                transaction_type = deposit.get('type', 'Unknown')
                created = deposit.get('created_at', 'Unknown')
                print(f"   Deposit {i+1}: ${amount/100:.2f} - {transaction_type} - {created}")
        else:
            print(f"   Response: {history}")
            
        return True
        
    except Exception as e:
        print(f"Error retrieving deposits: {e}")
        return False

if __name__ == "__main__":
    success = test_deposits()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")