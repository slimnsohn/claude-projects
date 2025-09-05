#!/usr/bin/env python3

"""
Find Washington State related markets
"""

import requests
import json

def find_wsu_markets():
    """Find all markets related to Washington State"""
    
    base_url = "https://api.elections.kalshi.com/trade-api/v2"
    
    # Get all NCAAF markets
    url = f"{base_url}/markets"
    params = {
        'series_ticker': 'KXNCAAFGAME',
        'limit': 200
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get('markets', [])
            
            print(f"Total NCAAF markets: {len(markets)}")
            
            # Search for Washington State related
            wsu_keywords = ['washington', 'wsu', 'state', 'cougar', 'san diego']
            wsu_markets = []
            
            for market in markets:
                ticker = market.get('ticker', '').lower()
                title = market.get('title', '').lower()
                yes_title = market.get('yes_sub_title', '').lower()
                no_title = market.get('no_sub_title', '').lower()
                
                for keyword in wsu_keywords:
                    if keyword in ticker or keyword in title or keyword in yes_title or keyword in no_title:
                        if market not in wsu_markets:
                            wsu_markets.append(market)
                        break
            
            print(f"\nFound {len(wsu_markets)} potentially related markets:")
            
            for market in wsu_markets:
                ticker = market.get('ticker', 'N/A')
                title = market.get('title', 'N/A')
                yes_sub = market.get('yes_sub_title', 'N/A')
                no_sub = market.get('no_sub_title', 'N/A')
                yes_ask = market.get('yes_ask', 'N/A')
                no_ask = market.get('no_ask', 'N/A')
                
                print(f"\nTicker: {ticker}")
                print(f"Title: {title}")
                print(f"Yes: {yes_sub} ({yes_ask}¢)")
                print(f"No: {no_sub} ({no_ask}¢)")
                
                # Check if this looks like WSU vs SDSU
                if ('washington' in title.lower() or 'cougar' in title.lower()) and ('san diego' in title.lower() or 'sdsu' in ticker.lower()):
                    print("*** POTENTIAL MATCH FOR WSU vs SDSU ***")
            
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_wsu_markets()