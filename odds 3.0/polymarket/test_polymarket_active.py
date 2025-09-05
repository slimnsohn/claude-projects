"""
Test Polymarket API to find active sports markets
"""

import requests
import json
from datetime import datetime

def test_active_sports_markets():
    """Find active sports markets on Polymarket"""
    
    base_url = "https://clob.polymarket.com"
    
    print("Searching for ACTIVE sports markets on Polymarket")
    print("="*60)
    
    # Test markets endpoint
    url = f"{base_url}/markets"
    params = {
        'limit': 500,  # Get many markets
        'active': 'true'  # Try to filter for active markets
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('data', [])
            print(f"Found {len(markets)} total markets")
            
            # Look for active sports markets
            active_sports_markets = []
            sports_keywords = ['nfl', 'mlb', 'nba', 'nhl', 'football', 'baseball', 'basketball', 'hockey', 'vs', 'chiefs', 'lakers', 'yankees', 'patriots']
            
            for market in markets:
                question = market.get('question', '').lower()
                market_slug = market.get('market_slug', '').lower()
                is_active = market.get('active', False)
                is_closed = market.get('closed', False)
                
                # Look for active sports markets
                if (any(keyword in question or keyword in market_slug for keyword in sports_keywords) 
                    and is_active and not is_closed):
                    active_sports_markets.append(market)
            
            print(f"\nFound {len(active_sports_markets)} ACTIVE sports markets:")
            print("-" * 60)
            
            if active_sports_markets:
                for i, market in enumerate(active_sports_markets[:10], 1):  # Show first 10
                    print(f"{i}. Question: {market.get('question', 'N/A')}")
                    print(f"   Slug: {market.get('market_slug', 'N/A')}")
                    print(f"   Active: {market.get('active', 'N/A')} | Closed: {market.get('closed', 'N/A')}")
                    
                    # Show token details and try to get prices
                    tokens = market.get('tokens', [])
                    if tokens:
                        print(f"   Tokens ({len(tokens)}):")
                        for token in tokens:
                            token_id = token.get('token_id', 'N/A')
                            outcome = token.get('outcome', 'N/A')
                            
                            # Try to get price for this token
                            try:
                                price_url = f"{base_url}/midpoint"
                                price_params = {'token_id': token_id}
                                price_response = requests.get(price_url, params=price_params, timeout=5)
                                
                                if price_response.status_code == 200:
                                    price_data = price_response.json()
                                    midpoint = price_data.get('midpoint', 'N/A')
                                    print(f"     - {outcome}: {midpoint} (ID: {token_id[:20]}...)")
                                else:
                                    print(f"     - {outcome}: No price available (ID: {token_id[:20]}...)")
                            except:
                                print(f"     - {outcome}: Price error (ID: {token_id[:20]}...)")
                    
                    print()
            else:
                print("No active sports markets found.")
                print("\nShowing first 10 active markets of any type:")
                active_markets = [m for m in markets if m.get('active', False) and not m.get('closed', False)]
                for i, market in enumerate(active_markets[:10], 1):
                    print(f"{i}. {market.get('question', 'N/A')}")
                    print(f"   Active: {market.get('active', 'N/A')} | Closed: {market.get('closed', 'N/A')}")
                    print(f"   Slug: {market.get('market_slug', 'N/A')}")
                    print()
                    
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_active_sports_markets()