"""
Test Kalshi connection and find MLB markets
"""

import requests
import json
from datetime import datetime

def test_kalshi_connection():
    """Test basic connection to Kalshi API"""
    print("TESTING KALSHI API CONNECTION")
    print("=" * 50)
    
    base_url = "https://api.kalshi.com/v1"
    headers = {'Accept': 'application/json'}
    
    # Test 1: Basic connection
    print("1. Testing basic API connection...")
    try:
        response = requests.get(f"{base_url}/markets", headers=headers, timeout=10, params={'limit': 1})
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Connection successful")
        else:
            print(f"   ❌ Connection failed: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return
    
    # Test 2: Search for MLB markets specifically
    print("\n2. Testing MLB market search...")
    try:
        params = {'series_ticker': 'KXMLBGAME', 'limit': 10}
        response = requests.get(f"{base_url}/markets", headers=headers, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('markets', [])
            print(f"   ✅ Found {len(markets)} MLB markets")
            
            if markets:
                print("\n   Sample MLB markets:")
                for i, market in enumerate(markets[:3]):
                    ticker = market.get('ticker', 'N/A')
                    title = market.get('title', 'N/A')
                    status = market.get('status', 'N/A')
                    last_price = market.get('last_price', 'N/A')
                    print(f"   {i+1}. {ticker}")
                    print(f"      Title: {title}")
                    print(f"      Status: {status}")
                    print(f"      Price: {last_price}")
                    print()
        else:
            print(f"   ❌ Failed to get MLB markets: {response.text}")
            
    except Exception as e:
        print(f"   ❌ MLB search error: {e}")
    
    # Test 3: Alternative search methods
    print("\n3. Testing alternative search methods...")
    
    # Try different search approaches
    search_methods = [
        {'search': 'baseball'},
        {'search': 'MLB'},  
        {'title': 'Winner'},
        {},  # All markets
    ]
    
    for i, params in enumerate(search_methods):
        try:
            params['limit'] = 20
            response = requests.get(f"{base_url}/markets", headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                markets = data.get('markets', [])
                
                # Count MLB-like markets
                mlb_count = 0
                for market in markets:
                    title = market.get('title', '').lower()
                    ticker = market.get('ticker', '').lower()
                    if 'winner' in title and ('vs' in title or 'at' in title):
                        mlb_count += 1
                
                print(f"   Method {i+1} ({params}): {len(markets)} markets, {mlb_count} potential games")
                
        except Exception as e:
            print(f"   Method {i+1} error: {e}")

if __name__ == "__main__":
    test_kalshi_connection()