#!/usr/bin/env python3

"""
Debug the actual cent values being received from Kalshi API
for the Washington State vs San Diego State game
"""

import requests
import json

def debug_wsu_sdsu_api_cents():
    """Check what cents the API is actually returning"""
    
    base_url = "https://api.elections.kalshi.com/trade-api/v2"
    
    # Get markets for WSU/SDSU
    url = f"{base_url}/markets"
    params = {
        'series_ticker': 'KXNCAAFGAME',
        'limit': 500
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('markets', [])
            
            # Find WSU/SDSU markets
            wsu_markets = [m for m in markets if 'SDSUWSU' in m.get('ticker', '')]
            
            print("KALSHI API VALUES FOR WSU vs SDSU")
            print("=" * 50)
            print("Expected from website: WSU 53\u00a2, SDSU 48\u00a2")
            print()
            
            if wsu_markets:
                print("API Market Data:")
                for market in wsu_markets:
                    ticker = market.get('ticker', '')
                    title = market.get('title', '')
                    yes_ask = market.get('yes_ask', 'N/A')
                    no_ask = market.get('no_ask', 'N/A')
                    last_price = market.get('last_price', 'N/A')
                    yes_bid = market.get('yes_bid', 'N/A')
                    no_bid = market.get('no_bid', 'N/A')
                    
                    print(f"\nTicker: {ticker}")
                    print(f"Title: {title}")
                    print(f"Yes Ask: {yes_ask}\u00a2 (what we use)")
                    print(f"Yes Bid: {yes_bid}\u00a2")
                    print(f"No Ask: {no_ask}\u00a2") 
                    print(f"No Bid: {no_bid}\u00a2")
                    print(f"Last Price: {last_price}\u00a2")
                    
                    # Determine team from ticker
                    if ticker.endswith('-WSU'):
                        print(f"  -> This is Washington St. market")
                        print(f"  -> We use yes_ask = {yes_ask}\u00a2")
                    elif ticker.endswith('-SDSU'):
                        print(f"  -> This is San Diego St. market")
                        print(f"  -> We use yes_ask = {yes_ask}\u00a2")
                
                # Test our conversion
                print(f"\n" + "="*50)
                print("CONVERSION TEST:")
                
                # Import our converter
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), 'kalshi_converter'))
                from converter import kalshi_cents_to_american_odds
                
                for market in wsu_markets:
                    ticker = market.get('ticker', '')
                    yes_ask = market.get('yes_ask', 50)
                    
                    if ticker.endswith('-WSU'):
                        team = "Washington St."
                        odds = kalshi_cents_to_american_odds(yes_ask)
                        print(f"{team}: {yes_ask}\u00a2 -> {odds}")
                    elif ticker.endswith('-SDSU'):
                        team = "San Diego St."  
                        odds = kalshi_cents_to_american_odds(yes_ask)
                        print(f"{team}: {yes_ask}\u00a2 -> {odds}")
                
                # Show expected
                print(f"\nExpected conversions:")
                print(f"Washington St.: 53\u00a2 -> {kalshi_cents_to_american_odds(53)}")
                print(f"San Diego St.: 48\u00a2 -> {kalshi_cents_to_american_odds(48)}")
                
            else:
                print("No WSU/SDSU markets found in API response")
                
        else:
            print(f"API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_wsu_sdsu_api_cents()