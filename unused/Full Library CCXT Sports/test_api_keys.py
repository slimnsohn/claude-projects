#!/usr/bin/env python3
"""
Test API Keys Directly
Direct testing of API keys to identify authentication issues.
"""

import asyncio
import sys
from pathlib import Path
import aiohttp
import traceback

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import load_environment_config


async def test_odds_api_directly():
    """Test The Odds API key directly"""
    print("=== TESTING THE ODDS API DIRECTLY ===")
    
    config = load_environment_config()
    odds_config = config.get('odds_api', {})
    api_key = odds_config.get('api_key')
    base_url = odds_config.get('base_url', 'https://api.the-odds-api.com/v4')
    
    print(f"API Key: {api_key[:8]}..." if api_key else "No API key found")
    print(f"Base URL: {base_url}")
    print()
    
    if not api_key:
        print("ERROR: No Odds API key found!")
        return False
    
    # Test direct API call
    test_url = f"{base_url}/sports"
    params = {
        'apiKey': api_key
    }
    
    print(f"Testing: {test_url}")
    print(f"Params: apiKey={api_key[:8]}...")
    print()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(test_url, params=params) as response:
                print(f"Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Response: Success - {len(data)} sports found")
                    print("Sample sports:", [sport.get('title', 'Unknown') for sport in data[:5]])
                    return True
                else:
                    text = await response.text()
                    print(f"Response Error: {text}")
                    return False
                    
    except Exception as e:
        print(f"Request failed: {e}")
        traceback.print_exc()
        return False


def test_kalshi_key_format():
    """Test Kalshi private key format"""
    print("=== TESTING KALSHI PRIVATE KEY FORMAT ===")
    
    config = load_environment_config()
    kalshi_config = config.get('kalshi', {})
    api_key = kalshi_config.get('api_key')
    private_key = kalshi_config.get('private_key')
    
    print(f"API Key: {api_key}")
    print(f"Private Key Length: {len(private_key) if private_key else 0}")
    print()
    
    if not private_key:
        print("ERROR: No private key found!")
        return False
    
    # Check if it starts and ends correctly
    if private_key.startswith('-----BEGIN RSA PRIVATE KEY-----'):
        print("OK: Private key has correct BEGIN marker")
    else:
        print("ERROR: Private key missing BEGIN marker")
        print(f"Starts with: {private_key[:50]}...")
        return False
    
    if private_key.endswith('-----END RSA PRIVATE KEY-----'):
        print("OK: Private key has correct END marker")
    else:
        print("ERROR: Private key missing END marker")
        print(f"Ends with: ...{private_key[-50:]}")
        return False
    
    # Test loading with cryptography
    try:
        from cryptography.hazmat.primitives import serialization
        
        private_key_obj = serialization.load_pem_private_key(
            private_key.encode('utf-8'),
            password=None
        )
        print("OK: Private key loaded successfully with cryptography")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to load private key - {e}")
        print("Private key preview:")
        print(private_key[:200] + "..." if len(private_key) > 200 else private_key)
        return False


async def main():
    """Test both API keys"""
    print("API KEY TESTING")
    print("=" * 50)
    print()
    
    # Test Kalshi key format
    kalshi_ok = test_kalshi_key_format()
    print()
    
    # Test Odds API key
    odds_ok = await test_odds_api_directly()
    print()
    
    # Summary
    print("=" * 50)
    print("SUMMARY:")
    print(f"Kalshi Private Key: {'OK' if kalshi_ok else 'FAILED'}")
    print(f"The Odds API Key: {'OK' if odds_ok else 'FAILED'}")
    
    if kalshi_ok and odds_ok:
        print("STATUS: Both API keys are working")
        return True
    else:
        print("STATUS: API key issues detected")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Test failed: {e}")
        traceback.print_exc()
        sys.exit(1)