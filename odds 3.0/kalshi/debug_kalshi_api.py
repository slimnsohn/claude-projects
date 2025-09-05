"""
Debug Kalshi API - See what data is actually coming through
"""

import requests
import json
from datetime import datetime

def test_kalshi_api():
    """Test Kalshi API endpoints and see raw data"""
    
    # Test both endpoints
    endpoints = [
        ("https://api.elections.kalshi.com/trade-api/v2", "Production"),
        ("https://demo-api.kalshi.co/trade-api/v2", "Demo")
    ]
    
    leagues = {
        'mlb': 'KXMLBGAME',
        'nfl': 'KXNFLGAME',
        'nba': 'KXNBAGAME',
        'nhl': 'KXNHLGAME'
    }
    
    for base_url, name in endpoints:
        print(f"\n{'='*80}")
        print(f"Testing {name} endpoint: {base_url}")
        print('='*80)
        
        for league, ticker in leagues.items():
            print(f"\n{league.upper()} ({ticker}):")
            print("-"*40)
            
            url = f"{base_url}/markets"
            params = {
                'series_ticker': ticker,
                'limit': 5,  # Just get first 5 for debugging
                'status': 'open'
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    markets = data.get('markets', [])
                    print(f"Found {len(markets)} markets")
                    
                    # Show first market details
                    if markets:
                        market = markets[0]
                        print(f"\nFirst market details:")
                        print(f"  Title: {market.get('title', 'N/A')}")
                        print(f"  Ticker: {market.get('ticker', 'N/A')}")
                        print(f"  Status: {market.get('status', 'N/A')}")
                        print(f"  Yes Ask: {market.get('yes_ask', 'N/A')}")
                        print(f"  Last Price: {market.get('last_price', 'N/A')}")
                        print(f"  Close Time: {market.get('close_time', 'N/A')}")
                        
                        # Show all market titles to understand structure
                        print(f"\nAll {len(markets)} market titles:")
                        for i, m in enumerate(markets, 1):
                            print(f"  {i}. {m.get('title', 'N/A')} [{m.get('ticker', 'N/A')}]")
                    else:
                        print("  No markets found!")
                else:
                    print(f"Error: {response.status_code}")
                    print(f"Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"Exception: {e}")
    
    # Also try without any filters
    print(f"\n{'='*80}")
    print("Testing without series_ticker filter:")
    print('='*80)
    
    url = "https://api.elections.kalshi.com/trade-api/v2/markets"
    params = {
        'limit': 10,
        'status': 'open'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('markets', [])
            print(f"Found {len(markets)} total open markets")
            
            # Show sports-related markets
            print("\nSports-related markets found:")
            sports_count = 0
            for market in markets:
                title = market.get('title', '')
                ticker = market.get('ticker', '')
                if any(sport in ticker.upper() for sport in ['MLB', 'NFL', 'NBA', 'NHL', 'GAME']):
                    sports_count += 1
                    print(f"  - {title} [{ticker}]")
                    if sports_count >= 10:
                        print("  ... (showing first 10)")
                        break
            
            if sports_count == 0:
                print("  No sports markets found")
                print("\nShowing first 5 markets of any type:")
                for i, market in enumerate(markets[:5], 1):
                    print(f"  {i}. {market.get('title', 'N/A')} [{market.get('ticker', 'N/A')}]")
                    
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_kalshi_api()