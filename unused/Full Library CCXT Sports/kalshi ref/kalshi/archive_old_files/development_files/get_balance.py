#!/usr/bin/env python3
"""
Get current account balance from Kalshi API
"""

import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from git_clients import KalshiHttpClient, Environment

def get_balance():
    """Get current account balance."""
    load_dotenv()
    env = Environment.PROD
    KEYID = os.getenv('DEMO_KEYID') if env == Environment.DEMO else os.getenv('PROD_KEYID')
    KEYFILE = os.getenv('DEMO_KEYFILE') if env == Environment.DEMO else os.getenv('PROD_KEYFILE')

    try:
        with open(KEYFILE, "rb") as key_file:
            private_key = serialization.load_pem_private_key(key_file.read(), password=None)
    except FileNotFoundError:
        raise FileNotFoundError(f"Private key file not found at {KEYFILE}")

    client = KalshiHttpClient(key_id=KEYID, private_key=private_key, environment=env)
    
    balance_response = client.get_balance()
    balance_cents = balance_response.get('balance', 0)
    balance_dollars = balance_cents / 100
    
    return {
        'balance_cents': balance_cents,
        'balance_dollars': balance_dollars,
        'raw_response': balance_response
    }

if __name__ == "__main__":
    result = get_balance()
    print(f"Current Balance: ${result['balance_dollars']:,.2f}")