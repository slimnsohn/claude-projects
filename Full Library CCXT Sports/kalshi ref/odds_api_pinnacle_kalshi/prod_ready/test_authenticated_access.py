#!/usr/bin/env python3
"""
Test if NFL markets require authentication
"""

import sys
import os
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.kalshi_client import KalshiClientUpdated as KalshiClient

def test_authenticated_access():
    """Test if we need to be logged in to see NFL markets"""
    
    print("TESTING AUTHENTICATED ACCESS TO NFL MARKETS")
    print("=" * 60)
    
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        creds_path = os.path.join(project_root, 'keys', 'kalshi_credentials.txt')
        client = KalshiClient(creds_path)
        
        # Test 1: Try to login and get session
        print("TEST 1: Attempting to login...")
        
        login_success = client.login()
        if login_success:
            print("  SUCCESS: Login successful")
            print(f"  Session token: {client.session_token[:20]}..." if client.session_token else "No token")
        else:
            print("  FAILED: Login failed")
            return
        
        # Test 2: Try authenticated requests with session token
        print(f"\nTEST 2: Making authenticated requests...")
        
        headers = {}
        if client.session_token:
            headers['Authorization'] = f'Bearer {client.session_token}'
        
        # Try different endpoints with authentication
        endpoints_to_try = [
            '/markets',
            '/markets?limit=1000',
            '/markets?category=sports',
            '/markets?status=active'
        ]
        
        for endpoint in endpoints_to_try:
            print(f"  Testing {endpoint}...")
            
            url = f"{client.base_url}{endpoint}"
            
            try:
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    markets = data.get('markets', [])
                    
                    # Look for NFL markets
                    nfl_markets = [m for m in markets if 'KXNFLGAME' in m.get('ticker', '')]
                    aug23_markets = [m for m in markets if 'AUG23' in m.get('ticker', '')]
                    
                    print(f"    Status: 200, Markets: {len(markets)}")
                    print(f"    NFL markets: {len(nfl_markets)}")
                    print(f"    Aug 23 markets: {len(aug23_markets)}")
                    
                    for nfl in nfl_markets:
                        print(f"      FOUND NFL: {nfl.get('ticker')} - {nfl.get('title')}")
                        
                else:
                    print(f"    Status: {response.status_code}")
                    if response.status_code == 401:
                        print(f"    Authentication required/failed")
                    elif response.status_code == 403:
                        print(f"    Access forbidden")
                        
            except Exception as e:
                print(f"    Error: {e}")
        
        # Test 3: Try to access the specific market directly
        print(f"\nTEST 3: Trying to access specific NFL market...")
        
        specific_ticker = "KXNFLGAME-25AUG23INDCIN"
        
        # Try different ways to access the specific market
        specific_endpoints = [
            f'/markets/{specific_ticker}',
            f'/markets?ticker={specific_ticker}',
            f'/events/kxnflgame'
        ]
        
        for endpoint in specific_endpoints:
            print(f"  Testing {endpoint}...")
            
            url = f"{client.base_url}{endpoint}"
            
            try:
                response = requests.get(url, headers=headers, timeout=30)
                
                print(f"    Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"    SUCCESS: Found market data")
                    print(f"    Data keys: {list(data.keys())}")
                    
                    if 'ticker' in data:
                        print(f"    Ticker: {data.get('ticker')}")
                        print(f"    Title: {data.get('title')}")
                elif response.status_code == 404:
                    print(f"    Market not found")
                elif response.status_code == 403:
                    print(f"    Access forbidden")
                    
            except Exception as e:
                print(f"    Error: {e}")
        
        print(f"\nCONCLUSION:")
        print("- Check if authentication gives access to different markets")
        print("- NFL markets might be in a different API section")
        print("- May need different API endpoints or parameters")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_authenticated_access()