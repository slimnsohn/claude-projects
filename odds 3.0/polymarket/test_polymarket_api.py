"""
Test Polymarket API to understand their sports market structure
"""

import requests
import json
from datetime import datetime

def test_polymarket_api():
    """Test Polymarket CLOB API to understand sports markets"""
    
    base_url = "https://clob.polymarket.com"
    
    print("Testing Polymarket CLOB API")
    print("="*60)
    
    # Test markets endpoint
    url = f"{base_url}/markets"
    params = {
        'limit': 50  # Get more markets to find sports
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('data', [])
            print(f"Found {len(markets)} markets")
            
            # Look for sports-related markets
            sports_markets = []
            sports_keywords = ['nfl', 'mlb', 'nba', 'nhl', 'football', 'baseball', 'basketball', 'hockey', 'sports', 'game', 'vs', 'match']
            
            for market in markets:
                question = market.get('question', '').lower()
                market_slug = market.get('market_slug', '').lower()
                
                if any(keyword in question or keyword in market_slug for keyword in sports_keywords):
                    sports_markets.append(market)
            
            print(f"\nFound {len(sports_markets)} sports-related markets:")
            print("-" * 60)
            
            for i, market in enumerate(sports_markets[:10], 1):  # Show first 10
                print(f"{i}. Question: {market.get('question', 'N/A')}")
                print(f"   Slug: {market.get('market_slug', 'N/A')}")
                print(f"   Active: {market.get('active', 'N/A')}")
                print(f"   Closed: {market.get('closed', 'N/A')}")
                
                # Show token details if available
                tokens = market.get('tokens', [])
                if tokens:
                    print(f"   Tokens: {len(tokens)} available")
                    for token in tokens[:2]:  # Show first 2 tokens
                        token_id = token.get('token_id', 'N/A')
                        outcome = token.get('outcome', 'N/A')
                        print(f"     - {outcome} (ID: {token_id})")
                
                print()
            
            if len(sports_markets) == 0:
                print("No sports markets found. Showing first 5 markets of any type:")
                for i, market in enumerate(markets[:5], 1):
                    print(f"{i}. {market.get('question', 'N/A')} [{market.get('market_slug', 'N/A')}]")
                    
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"Exception: {e}")

    # Test getting token prices for sports markets
    print("\n" + "="*60)
    print("Testing token price endpoint")
    print("="*60)
    
    # Try to get some token IDs from sports markets and test pricing
    try:
        # This is a hypothetical token ID - we'd need actual ones from above
        test_url = f"{base_url}/midpoint"
        params = {'token_id': '123456'}  # Would need real token ID
        
        response = requests.get(test_url, params=params, timeout=10)
        print(f"Midpoint endpoint status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Note: Need valid token_id for price testing")
            
    except Exception as e:
        print(f"Price test exception: {e}")

if __name__ == "__main__":
    test_polymarket_api()