#!/usr/bin/env python3

"""
Debug how markets are assigned to teams for WSU vs SDSU
"""

import sys
import os
import requests
sys.path.append(os.path.dirname(__file__))

from kalshi.client import KalshiClient

def debug_wsu_market_assignment():
    """Debug the market assignment for WSU vs SDSU"""
    
    # Get the actual markets from Kalshi API
    base_url = "https://api.elections.kalshi.com/trade-api/v2"
    
    # Get markets for this game
    url = f"{base_url}/markets"
    params = {
        'series_ticker': 'KXNCAAFGAME',
        'limit': 100
    }
    
    response = requests.get(url, params=params, timeout=30)
    if response.status_code != 200:
        print("Failed to get markets")
        return
    
    data = response.json()
    markets = data.get('markets', [])
    
    # Find WSU/SDSU markets
    wsu_markets = [m for m in markets if 'SDSUWSU' in m.get('ticker', '')]
    
    print(f"Found {len(wsu_markets)} WSU/SDSU markets:")
    
    for market in wsu_markets:
        ticker = market.get('ticker', '')
        title = market.get('title', '')
        yes_sub = market.get('yes_sub_title', '')
        no_sub = market.get('no_sub_title', '')
        yes_ask = market.get('yes_ask', 0)
        no_ask = market.get('no_ask', 0)
        
        print(f"\nMarket: {ticker}")
        print(f"Title: {title}")
        print(f"Yes Sub: {yes_sub} ({yes_ask}¢)")
        print(f"No Sub: {no_sub} ({no_ask}¢)")
    
    # Now test how our client processes this
    print(f"\n" + "="*50)
    print("TESTING CLIENT PROCESSING:")
    
    client = KalshiClient()
    
    # Parse the teams first
    game_id = "SDSUWSU" 
    game_info = client._parse_college_teams(game_id)
    
    if game_info:
        print(f"Game info:")
        print(f"  Home team: {game_info['home_team']}")
        print(f"  Away team: {game_info['away_team']}")
        
        # Test odds extraction
        odds = client._extract_odds_from_markets(wsu_markets, game_info)
        print(f"Extracted odds:")
        print(f"  Home odds: {odds[0]}")
        print(f"  Away odds: {odds[1]}")
        
        # Test market matching logic
        print(f"\nMarket matching logic:")
        for market in wsu_markets:
            ticker = market.get('ticker', '')
            title = market.get('title', '')
            yes_ask = market.get('yes_ask', 0)
            
            print(f"\nMarket: {ticker}")
            print(f"Title: {title}")
            print(f"Yes Ask: {yes_ask}¢")
            
            # Check if home team matches
            home_match = game_info['home_team'] in ticker or game_info['home_team'] in title
            away_match = game_info['away_team'] in ticker or game_info['away_team'] in title
            
            print(f"Home team '{game_info['home_team']}' in ticker: {'YES' if home_match else 'NO'}")
            print(f"Away team '{game_info['away_team']}' in ticker: {'YES' if away_match else 'NO'}")
            
            if home_match:
                american_odds = client._kalshi_cents_to_american(yes_ask)
                print(f"-> This would be HOME odds: {american_odds}")
            elif away_match:
                american_odds = client._kalshi_cents_to_american(yes_ask)
                print(f"-> This would be AWAY odds: {american_odds}")

if __name__ == "__main__":
    debug_wsu_market_assignment()