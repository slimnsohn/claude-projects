#!/usr/bin/env python3

"""
Debug the exact odds extraction for WSU vs SDSU
"""

import sys
import os
import requests
sys.path.append(os.path.dirname(__file__))

from kalshi.client import KalshiClient

def debug_exact_odds_extraction():
    """Debug the exact odds extraction process"""
    
    # Get the actual markets
    base_url = "https://api.elections.kalshi.com/trade-api/v2"
    url = f"{base_url}/markets"
    params = {
        'series_ticker': 'KXNCAAFGAME',
        'limit': 500
    }
    
    response = requests.get(url, params=params, timeout=30)
    if response.status_code != 200:
        print("Failed to get markets")
        return
    
    data = response.json()
    all_markets = data.get('markets', [])
    
    # Find WSU/SDSU markets
    wsu_markets = [m for m in all_markets if 'SDSUWSU' in m.get('ticker', '')]
    
    if not wsu_markets:
        print("No WSU/SDSU markets found")
        return
    
    print(f"Found {len(wsu_markets)} WSU/SDSU markets before sorting:")
    for i, market in enumerate(wsu_markets):
        ticker = market.get('ticker', '')
        yes_ask = market.get('yes_ask', 0)
        print(f"  {i}: {ticker} -> {yes_ask}¢")
    
    # Sort like the client does
    sorted_markets = sorted(wsu_markets, key=lambda x: x.get('ticker', ''))
    
    print(f"\nAfter sorting:")
    for i, market in enumerate(sorted_markets):
        ticker = market.get('ticker', '')
        yes_ask = market.get('yes_ask', 0)
        print(f"  {i}: {ticker} -> {yes_ask}¢")
    
    # Test team parsing
    client = KalshiClient()
    game_id = "SDSUWSU"
    game_info = client._parse_college_teams(game_id)
    
    if game_info:
        print(f"\nParsed teams:")
        print(f"  Home: {game_info['home_team']}")
        print(f"  Away: {game_info['away_team']}")
        
        # Test odds extraction step by step
        print(f"\nTesting odds extraction:")
        
        home_odds = None
        away_odds = None
        
        for i, market in enumerate(sorted_markets):
            ticker = market.get('ticker', '')
            title = market.get('title', '')
            yes_ask = market.get('yes_ask', 50)
            
            print(f"\n  Market {i}: {ticker}")
            print(f"    Title: {title}")
            print(f"    Yes Ask: {yes_ask}¢")
            
            # Test matching logic
            home_in_ticker = game_info['home_team'] in ticker
            home_in_title = game_info['home_team'] in title
            away_in_ticker = game_info['away_team'] in ticker  
            away_in_title = game_info['away_team'] in title
            
            print(f"    Home team '{game_info['home_team']}' in ticker: {home_in_ticker}")
            print(f"    Home team '{game_info['home_team']}' in title: {home_in_title}")
            print(f"    Away team '{game_info['away_team']}' in ticker: {away_in_ticker}")
            print(f"    Away team '{game_info['away_team']}' in title: {away_in_title}")
            
            if home_in_ticker or home_in_title:
                american_odds = client._kalshi_cents_to_american(yes_ask)
                print(f"    -> ASSIGNED TO HOME: {american_odds}")
                home_odds = american_odds
            elif away_in_ticker or away_in_title:
                american_odds = client._kalshi_cents_to_american(yes_ask)
                print(f"    -> ASSIGNED TO AWAY: {american_odds}")
                away_odds = american_odds
        
        # Check fallback logic
        if home_odds is None or away_odds is None:
            print(f"\n  FALLBACK ASSIGNMENT:")
            print(f"    Home was None: {home_odds is None}")
            print(f"    Away was None: {away_odds is None}")
            
            if len(sorted_markets) >= 2:
                fallback_home = client._kalshi_cents_to_american(sorted_markets[0].get('yes_ask', 50))
                fallback_away = client._kalshi_cents_to_american(sorted_markets[1].get('yes_ask', 50))
                print(f"    Fallback home (market 0): {fallback_home} from {sorted_markets[0].get('yes_ask', 50)}¢")
                print(f"    Fallback away (market 1): {fallback_away} from {sorted_markets[1].get('yes_ask', 50)}¢")
                
                if home_odds is None:
                    home_odds = fallback_home
                if away_odds is None:
                    away_odds = fallback_away
        
        print(f"\nFINAL ASSIGNMENT:")
        print(f"  Home ({game_info['home_team']}): {home_odds}")
        print(f"  Away ({game_info['away_team']}): {away_odds}")
        
        # Check which one becomes favorite/dog
        if home_odds and away_odds:
            if home_odds < away_odds:
                print(f"  -> {game_info['home_team']} is FAVORITE ({home_odds})")
                print(f"  -> {game_info['away_team']} is DOG ({away_odds})")
            else:
                print(f"  -> {game_info['away_team']} is FAVORITE ({away_odds})")
                print(f"  -> {game_info['home_team']} is DOG ({home_odds})")

if __name__ == "__main__":
    debug_exact_odds_extraction()