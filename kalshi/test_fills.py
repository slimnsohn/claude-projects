#!/usr/bin/env python3
"""
Test script to check if we can retrieve fills using git_clients.py
"""

import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from git_clients import KalshiHttpClient, Environment

# Load environment variables
load_dotenv()
env = Environment.PROD
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

def test_fills():
    """Test retrieving fills."""
    print("=" * 60)
    print("TESTING FILLS RETRIEVAL")
    print("=" * 60)
    
    try:
        # Test balance first to confirm connection
        print("1. Testing balance...")
        balance = client.get_balance()
        print(f"   Balance: ${balance.get('balance', 0) / 100:.2f}")
        
        print("\n2. Testing fills...")
        fills = client.get_fills(limit=10)
        
        print(f"   Response: {fills}")
            
        return True
        
    except Exception as e:
        print(f"Error retrieving fills: {e}")
        return False

if __name__ == "__main__":
    success = test_fills()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")