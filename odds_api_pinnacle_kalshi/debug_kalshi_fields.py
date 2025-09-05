#!/usr/bin/env python3

"""
Debug script to see what fields are available in Kalshi market data
"""

import requests
import json

def debug_kalshi_market_fields():
    """Check what fields are available in Kalshi market responses"""
    
    base_url = "https://api.elections.kalshi.com/trade-api/v2"
    series_ticker = "KXNCAAFGAME"  # NCAAF games
    
    # Fetch a few markets
    url = f"{base_url}/markets"
    params = {
        'series_ticker': series_ticker,
        'limit': 5  # Just get a few for debugging
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('markets', [])
            
            print(f"Found {len(markets)} markets")
            
            if markets:
                print("\nFirst market fields:")
                market = markets[0]
                
                print(f"Available fields: {list(market.keys())}")
                
                print(f"\nSample market data:")
                for key, value in market.items():
                    print(f"  {key}: {value}")
                    
                # Look specifically for price-related fields
                print(f"\nPrice-related fields:")
                price_fields = [k for k in market.keys() if any(term in k.lower() for term in ['price', 'ask', 'bid', 'yes', 'no'])]
                for field in price_fields:
                    print(f"  {field}: {market[field]}")
                    
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_kalshi_market_fields()