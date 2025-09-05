"""
Debug Polymarket API specifically for NFL games
Test different search approaches to find active NFL markets
"""

import requests
import json
from datetime import datetime

def debug_polymarket_nfl():
    """Look for NFL markets on Polymarket with different approaches"""
    
    base_url = "https://clob.polymarket.com"
    
    print("=== POLYMARKET NFL MARKET DEBUG ===")
    print("Testing different search approaches...")
    print("="*60)
    
    # Approach 1: Search ALL markets for NFL-related content
    url = f"{base_url}/markets"
    params = {
        'limit': 1000  # Get lots of markets
    }
    
    try:
        print("\n1. Searching through ALL markets for NFL content...")
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('data', [])
            print(f"Total markets retrieved: {len(markets)}")
            
            # Look for NFL markets with different keywords
            nfl_keywords = [
                'nfl', 'football', 'chiefs', 'patriots', 'cowboys', 'packers', 
                'steelers', 'ravens', 'eagles', '49ers', 'rams', 'bills',
                'bengals', 'dolphins', 'jets', 'giants', 'broncos', 'raiders',
                'chargers', 'colts', 'titans', 'jaguars', 'texans', 'browns',
                'lions', 'bears', 'vikings', 'saints', 'falcons', 'panthers',
                'buccaneers', 'cardinals', 'seahawks', 'sunday', 'monday night'
            ]
            
            nfl_markets = []
            for market in markets:
                question = market.get('question', '').lower()
                market_slug = market.get('market_slug', '').lower()
                
                if any(keyword in question or keyword in market_slug for keyword in nfl_keywords):
                    nfl_markets.append(market)
            
            print(f"Found {len(nfl_markets)} NFL-related markets")
            
            if nfl_markets:
                print("\nFirst 20 NFL markets found:")
                print("-" * 80)
                
                for i, market in enumerate(nfl_markets[:20], 1):
                    question = market.get('question', 'N/A')
                    slug = market.get('market_slug', 'N/A')
                    active = market.get('active', False)
                    closed = market.get('closed', True)
                    tokens = market.get('tokens', [])
                    
                    status = "ACTIVE" if active and not closed else "CLOSED"
                    
                    print(f"{i:2d}. [{status}] {question}")
                    print(f"     Slug: {slug}")
                    print(f"     Tokens: {len(tokens)}")
                    
                    # If active, try to get token prices
                    if active and not closed and tokens:
                        print("     Prices:", end=" ")
                        for token in tokens[:2]:  # First 2 tokens
                            token_id = token.get('token_id')
                            outcome = token.get('outcome', 'Unknown')
                            
                            if token_id:
                                try:
                                    price_url = f"{base_url}/midpoint"
                                    price_params = {'token_id': token_id}
                                    price_resp = requests.get(price_url, params=price_params, timeout=3)
                                    
                                    if price_resp.status_code == 200:
                                        price_data = price_resp.json()
                                        midpoint = price_data.get('midpoint', 'N/A')
                                        print(f"{outcome}={midpoint}", end=" ")
                                    else:
                                        print(f"{outcome}=No price", end=" ")
                                except:
                                    print(f"{outcome}=Error", end=" ")
                        print()  # New line
                    
                    print()
            else:
                print("No NFL markets found with keyword search!")
    
        else:
            print(f"Error fetching markets: {response.status_code}")
            print(response.text[:500])
            
    except Exception as e:
        print(f"Exception in market search: {e}")

    # Approach 2: Try different API endpoints
    print("\n" + "="*60)
    print("2. Testing alternative endpoints...")
    
    # Try gamma API if it exists
    gamma_endpoints = [
        "https://gamma-api.polymarket.com/markets",
        f"{base_url}/events", 
        f"{base_url}/sports",
        f"{base_url}/categories"
    ]
    
    for endpoint in gamma_endpoints:
        try:
            print(f"\nTrying endpoint: {endpoint}")
            response = requests.get(endpoint, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Response type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"Keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"List length: {len(data)}")
                        if data:
                            print(f"First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not dict'}")
                except:
                    print("Response not JSON")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_polymarket_nfl()