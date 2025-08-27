"""
Test Kalshi authentication methods and API endpoints
"""

import requests
import json

def load_credentials():
    credentials = {}
    with open("keys/kalshi_credentials.txt", 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                credentials[key] = value
    return credentials

def test_kalshi_endpoints():
    """Test different Kalshi API endpoints and authentication methods"""
    credentials = load_credentials()
    
    base_urls = [
        "https://trading-api.kalshi.com/trade-api/v2",
        "https://demo-api.kalshi.co/trade-api/v2",
        "https://api.kalshi.com/v1"
    ]
    
    print("Testing Kalshi API endpoints...")
    print(f"Email: {credentials.get('KALSHI_EMAIL', 'Not found')}")
    print(f"API Key: {credentials.get('KALSHI_API_KEY', 'Not found')[:20]}...")
    
    for base_url in base_urls:
        print(f"\n=== Testing {base_url} ===")
        
        # Test 1: Public endpoint (should work without auth)
        try:
            public_url = f"{base_url}/markets"
            print(f"Testing public markets endpoint...")
            response = requests.get(public_url, timeout=10)
            print(f"Public endpoint status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Success: Found {len(data.get('markets', []))} markets")
            else:
                print(f"Error: {response.text[:200]}")
        except Exception as e:
            print(f"Public endpoint exception: {e}")
        
        # Test 2: Email/Password authentication
        try:
            login_url = f"{base_url}/login"
            login_data = {
                "email": credentials.get('KALSHI_EMAIL'),
                "password": credentials.get('KALSHI_PASSWORD')
            }
            print(f"Testing email/password login...")
            response = requests.post(login_url, json=login_data, timeout=10)
            print(f"Login status: {response.status_code}")
            
            if response.status_code == 200:
                auth_data = response.json()
                print(f"Login success: {list(auth_data.keys())}")
                token = auth_data.get('token')
                if token:
                    print(f"Token received: {token[:20]}...")
                    # Test authenticated endpoint
                    headers = {'Authorization': f'Bearer {token}'}
                    auth_response = requests.get(f"{base_url}/portfolio/balance", headers=headers, timeout=10)
                    print(f"Authenticated request status: {auth_response.status_code}")
            else:
                print(f"Login error: {response.text}")
                
        except Exception as e:
            print(f"Login exception: {e}")
    
    # Test 3: Alternative authentication patterns
    print(f"\n=== Testing Alternative Auth Patterns ===")
    try:
        # Some APIs use different field names
        alt_login_data = {
            "username": credentials.get('KALSHI_EMAIL'),
            "password": credentials.get('KALSHI_PASSWORD')
        }
        response = requests.post("https://trading-api.kalshi.com/trade-api/v2/login", json=alt_login_data, timeout=10)
        print(f"Alternative login format status: {response.status_code}")
        
        # Try with API key in header
        headers = {'X-API-Key': credentials.get('KALSHI_API_KEY')}
        response = requests.get("https://trading-api.kalshi.com/trade-api/v2/markets", headers=headers, timeout=10)
        print(f"API key header status: {response.status_code}")
        
    except Exception as e:
        print(f"Alternative auth exception: {e}")

def test_market_search():
    """Test if we can fetch any markets without authentication"""
    urls = [
        "https://trading-api.kalshi.com/trade-api/v2/markets",
        "https://demo-api.kalshi.co/trade-api/v2/markets",
        "https://api.kalshi.com/v1/markets"
    ]
    
    print(f"\n=== Testing Market Endpoints (No Auth) ===")
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"{url}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Success: {len(data.get('markets', data.get('data', [])))} items")
        except Exception as e:
            print(f"  Exception: {e}")

if __name__ == "__main__":
    test_kalshi_endpoints()
    test_market_search()