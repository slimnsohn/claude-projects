#!/usr/bin/env python3

"""
Debug script to check the Washington State vs San Diego State market specifically
"""

import requests
import json

def debug_wsu_sdsu_market():
    """Check the specific WSU vs SDSU market data"""
    
    base_url = "https://api.elections.kalshi.com/trade-api/v2"
    
    # The ticker from the URL
    target_ticker = "KXNCAAFGAME-25SEP06SDSUWSU"
    
    # Get the specific market
    url = f"{base_url}/markets/{target_ticker}"
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            market = response.json()
            
            print(f"Market: {target_ticker}")
            print(f"Title: {market.get('title', 'N/A')}")
            print(f"Yes Sub Title: {market.get('yes_sub_title', 'N/A')}")
            print(f"No Sub Title: {market.get('no_sub_title', 'N/A')}")
            print()
            
            # Price information
            print("CURRENT PRICES:")
            print(f"Yes Ask: {market.get('yes_ask', 'N/A')}¢")
            print(f"Yes Bid: {market.get('yes_bid', 'N/A')}¢") 
            print(f"No Ask: {market.get('no_ask', 'N/A')}¢")
            print(f"No Bid: {market.get('no_bid', 'N/A')}¢")
            print(f"Last Price: {market.get('last_price', 'N/A')}¢")
            print()
            
            # Calculate percentages
            yes_ask = market.get('yes_ask', 0)
            no_ask = market.get('no_ask', 0)
            
            if yes_ask and no_ask:
                print("ASK PRICE PERCENTAGES:")
                print(f"Yes team ({market.get('yes_sub_title', 'Team 1')}): {yes_ask}¢ ({yes_ask}%)")
                print(f"No team (opponent): {no_ask}¢ ({no_ask}%)")
                print(f"Total: {yes_ask + no_ask}¢")
                
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
            # Try searching for markets containing WSU or SDSU
            print("\nSearching for WSU/SDSU markets...")
            search_url = f"{base_url}/markets"
            params = {
                'series_ticker': 'KXNCAAFGAME',
                'limit': 50
            }
            
            search_response = requests.get(search_url, params=params, timeout=30)
            if search_response.status_code == 200:
                data = search_response.json()
                markets = data.get('markets', [])
                
                wsu_markets = [m for m in markets if 'WSU' in m.get('ticker', '') or 'Washington' in m.get('title', '')]
                print(f"Found {len(wsu_markets)} WSU-related markets")
                
                for market in wsu_markets[:3]:  # Show first 3
                    print(f"  {market.get('ticker', 'N/A')}: {market.get('title', 'N/A')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_wsu_sdsu_market()