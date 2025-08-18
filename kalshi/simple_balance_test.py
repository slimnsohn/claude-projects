#!/usr/bin/env python3
"""
Simple test to get portfolio balance working with correct signature.
"""

import os
import time
import base64
import json
import requests
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

load_dotenv()

def load_private_key():
    """Load private key from .env file."""
    # Read private key directly from file
    with open('.env', 'r') as f:
        content = f.read()
    
    # Extract private key
    start = content.find('KALSHI_PRIVATE_KEY=') + len('KALSHI_PRIVATE_KEY=')
    end = content.find('\n\n', start)
    if end == -1:
        end = content.find('\n#', start)
    if end == -1:
        end = len(content)
    
    private_key_text = content[start:end].strip()
    
    # Load the key
    private_key = serialization.load_pem_private_key(
        private_key_text.encode('utf-8'),
        password=None
    )
    return private_key

def test_balance():
    """Test getting portfolio balance with different signature methods."""
    api_key = os.getenv('KALSHI_API_KEY')
    private_key = load_private_key()
    
    print(f"API Key: {api_key}")
    print(f"Private Key loaded: {private_key is not None}")
    
    url = "https://api.elections.kalshi.com/trade-api/v2/portfolio/balance"
    timestamp = str(int(time.time() * 1000))
    method = "GET"
    path = "/portfolio/balance"
    body = ""
    
    # Create message
    message = f"{timestamp}{method}{path}{body}"
    print(f"Message to sign: '{message}'")
    
    # Try different signature methods
    methods = [
        ("PKCS1v15", lambda: private_key.sign(
            message.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )),
        ("PSS_DIGEST", lambda: private_key.sign(
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH
            ),
            hashes.SHA256()
        )),
        ("PSS_MAX", lambda: private_key.sign(
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        ))
    ]
    
    for method_name, sign_func in methods:
        try:
            signature_bytes = sign_func()
            signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
            
            headers = {
                "KALSHI-ACCESS-KEY": api_key,
                "KALSHI-ACCESS-TIMESTAMP": timestamp,
                "KALSHI-ACCESS-SIGNATURE": signature_b64,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            print(f"\nTrying {method_name}...")
            print(f"Signature: {signature_b64[:50]}...")
            
            response = requests.get(url, headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print(f"SUCCESS with {method_name}!")
                return response.json()
            elif response.status_code != 401:
                print(f"Different error with {method_name}: {response.status_code}")
                
        except Exception as e:
            print(f"Error with {method_name}: {e}")
    
    print("All signature methods failed.")
    return None

if __name__ == "__main__":
    result = test_balance()