"""
Test Polymarket API with different parameters to find active NFL markets
"""

import requests
import json
from datetime import datetime, timedelta

def test_polymarket_active_search():
    """Test different approaches to find active NFL markets"""
    
    base_url = "https://clob.polymarket.com"
    gamma_url = "https://gamma-api.polymarket.com"
    
    print("=== TESTING POLYMARKET ACTIVE MARKET DISCOVERY ===")
    print("="*70)
    
    # Test 1: CLOB API with different parameters
    print("\n1. Testing CLOB API with various parameters...")
    
    test_params = [
        {'limit': 1000, 'active': True},
        {'limit': 1000, 'closed': False},
        {'limit': 1000},  # No filters
        {'limit': 200, 'active': True, 'closed': False},
    ]
    
    for i, params in enumerate(test_params, 1):
        try:
            print(f"\n  Test {i}: {params}")
            response = requests.get(f"{base_url}/markets", params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                markets = data.get('data', [])
                print(f"    Status: {response.status_code}, Markets: {len(markets)}")
                
                # Look for NFL markets
                nfl_active = 0
                nfl_total = 0
                for market in markets:
                    question = market.get('question', '').lower()
                    if 'nfl' in question or 'football' in question or any(team in question for team in ['chiefs', 'ravens', 'bills']):
                        nfl_total += 1
                        if market.get('active', False) and not market.get('closed', True):
                            nfl_active += 1
                            print(f"    ACTIVE NFL: {market.get('question')}")
                
                print(f"    NFL markets: {nfl_total} total, {nfl_active} active")
            else:
                print(f"    Status: {response.status_code}")
                
        except Exception as e:
            print(f"    Error: {e}")
    
    # Test 2: Try Gamma API with different approaches
    print(f"\n2. Testing Gamma API...")
    
    try:
        response = requests.get(f"{gamma_url}/markets", timeout=15)
        if response.status_code == 200:
            markets = response.json()
            print(f"  Gamma markets: {len(markets)}")
            
            # Look for any active markets
            active_count = 0
            sports_count = 0
            for market in markets:
                if market.get('active', False) and not market.get('closed', True):
                    active_count += 1
                    question = market.get('question', '')
                    if any(word in question.lower() for word in ['nfl', 'football', 'ravens', 'bills', 'chiefs']):
                        sports_count += 1
                        print(f"  ACTIVE SPORTS: {question}")
            
            print(f"  Active markets: {active_count}, Active sports: {sports_count}")
        else:
            print(f"  Gamma status: {response.status_code}")
            
    except Exception as e:
        print(f"  Gamma error: {e}")
    
    # Test 3: Try to access specific event endpoint format
    print(f"\n3. Testing event-specific endpoints...")
    
    # Based on the URL you provided: https://polymarket.com/event/nfl-bal-buf-2025-09-07
    event_slugs = [
        'nfl-bal-buf-2025-09-07',
        'nfl-chiefs-vs-raiders', 
        'nfl-ravens-bills'
    ]
    
    for slug in event_slugs:
        try:
            # Try different endpoint patterns
            endpoints = [
                f"{base_url}/events/{slug}",
                f"{base_url}/markets?event={slug}",
                f"{gamma_url}/events/{slug}",
                f"https://strapi-matic.polymarket.com/events?slug={slug}"
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=10)
                    print(f"  {endpoint} -> {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            if isinstance(data, dict):
                                print(f"    Keys: {list(data.keys())[:5]}")
                            elif isinstance(data, list) and data:
                                print(f"    List length: {len(data)}")
                        except:
                            print(f"    Not JSON response")
                except:
                    pass
                    
        except Exception as e:
            print(f"  Error testing {slug}: {e}")

    # Test 4: Try different base URLs that might work
    print(f"\n4. Testing alternative API endpoints...")
    
    alt_urls = [
        "https://strapi-matic.polymarket.com/markets",
        "https://api.polymarket.com/markets",
        "https://data-api.polymarket.com/markets"
    ]
    
    for url in alt_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"  {url} -> {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"    Found {len(data)} items")
                    elif isinstance(data, dict):
                        print(f"    Dict keys: {list(data.keys())[:3]}")
                except:
                    print(f"    Response not JSON")
                    
        except Exception as e:
            print(f"    Error: {e}")

if __name__ == "__main__":
    test_polymarket_active_search()