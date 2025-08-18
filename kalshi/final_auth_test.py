#!/usr/bin/env python3
"""
Final test using exact Kalshi documentation format.
"""

import os
import time
import base64
import hashlib
import requests
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

load_dotenv()

def test_exact_kalshi_format():
    """Test using the exact format from Kalshi documentation."""
    
    # Load credentials
    api_key = os.getenv('KALSHI_API_KEY')
    
    # Load private key from file
    with open('.env', 'r') as f:
        content = f.read()
    
    start = content.find('KALSHI_PRIVATE_KEY=') + len('KALSHI_PRIVATE_KEY=')
    end = content.find('\n\n', start)
    if end == -1:
        end = content.find('\n#', start)
    if end == -1:
        end = len(content)
    
    private_key_text = content[start:end].strip()
    private_key = serialization.load_pem_private_key(
        private_key_text.encode('utf-8'),
        password=None
    )
    
    print(f"Testing with API Key: {api_key}")
    
    # Test different message constructions
    timestamp = str(int(time.time() * 1000))
    method = "GET"
    path = "/portfolio/balance"
    body = ""
    
    # Try different message formats
    message_formats = [
        f"{timestamp}{method}{path}{body}",  # Current format
        f"{timestamp}{method}{path}",        # Without body
        f"{timestamp} {method} {path} {body}",  # With spaces
        f"{timestamp}\n{method}\n{path}\n{body}",  # With newlines
    ]
    
    url = "https://api.elections.kalshi.com/trade-api/v2/portfolio/balance"
    
    for i, message in enumerate(message_formats):
        print(f"\nTrying format {i+1}: '{repr(message)}'")
        
        try:
            # Use PSS with DIGEST_LENGTH (most common)
            signature_bytes = private_key.sign(
                message.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.DIGEST_LENGTH
                ),
                hashes.SHA256()
            )
            
            signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
            
            headers = {
                "KALSHI-ACCESS-KEY": api_key,
                "KALSHI-ACCESS-TIMESTAMP": timestamp,
                "KALSHI-ACCESS-SIGNATURE": signature_b64,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("SUCCESS! Found working format!")
                print(f"Response: {response.json()}")
                return True
            elif response.status_code == 401:
                error_msg = response.json().get('error', {}).get('details', '')
                if 'INCORRECT_API_KEY_SIGNATURE' not in error_msg:
                    print(f"Different auth error: {error_msg}")
            else:
                print(f"Response: {response.text[:100]}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nAll message formats failed. The issue might be:")
    print("1. API key and private key are not from the same generation")
    print("2. Account doesn't have API access enabled")
    print("3. Need to contact Kalshi support")
    
    return False

if __name__ == "__main__":
    success = test_exact_kalshi_format()
    if not success:
        print("\n" + "="*50)
        print("RECOMMENDATION:")
        print("1. Go to https://kalshi.com/account/profile")
        print("2. Delete your current API key")
        print("3. Generate a completely new API key pair")
        print("4. Update .env with the new credentials")
        print("5. If still fails, contact Kalshi support")
        print("="*50)