#!/usr/bin/env python3
"""
Debug script to find actual NFL games on Kalshi
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.kalshi_client import KalshiClientUpdated as KalshiClient

def search_for_nfl_games():
    """Search for actual NFL games using different strategies"""
    
    print("DEBUGGING NFL GAME SEARCH ON KALSHI")
    print("=" * 60)
    
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        creds_path = os.path.join(project_root, 'keys', 'kalshi_credentials.txt')
        client = KalshiClient(creds_path)
        
        # Get all markets
        all_markets = client._get_all_markets_paginated()
        all_markets_data = all_markets.get('data', [])
        
        print(f"Searching through {len(all_markets_data)} total markets...")
        print()
        
        # Strategy 1: Look for NFL team names in titles
        nfl_teams = [
            'patriots', 'cowboys', 'steelers', 'packers', 'giants', 'eagles', 
            'broncos', 'seahawks', 'chiefs', 'raiders', 'chargers', 'rams',
            'saints', 'falcons', 'panthers', 'buccaneers', 'dolphins', 'jets',
            'bills', 'ravens', 'browns', 'bengals', 'titans', 'colts',
            'jaguars', 'texans', 'bears', 'lions', 'vikings', 'cardinals'
        ]
        
        print("STRATEGY 1: Searching for NFL team names in titles...")
        team_matches = []
        for market in all_markets_data:
            title = market.get('title', '').lower()
            ticker = market.get('ticker', '').lower()
            
            # Check if title contains NFL team names
            for team in nfl_teams:
                if team in title and ('winner' in title or 'win' in title):
                    team_matches.append(market)
                    break
        
        print(f"Found {len(team_matches)} markets with NFL team names")
        for i, market in enumerate(team_matches[:10], 1):  # Show first 10
            print(f"{i:2d}. {market.get('ticker')}: {market.get('title')}")
        
        if len(team_matches) > 10:
            print(f"... and {len(team_matches) - 10} more")
        
        print()
        
        # Strategy 2: Look for specific ticker patterns
        print("STRATEGY 2: Looking for game-like ticker patterns...")
        game_patterns = ['game', 'nfl', 'football']
        
        ticker_matches = []
        for market in all_markets_data:
            ticker = market.get('ticker', '').lower()
            title = market.get('title', '').lower()
            
            # Look for game-related tickers
            if any(pattern in ticker for pattern in game_patterns):
                if 'winner' in title or 'win' in title:
                    ticker_matches.append(market)
        
        print(f"Found {len(ticker_matches)} markets with game-like tickers")
        for i, market in enumerate(ticker_matches[:10], 1):  # Show first 10
            print(f"{i:2d}. {market.get('ticker')}: {market.get('title')}")
        
        if len(ticker_matches) > 10:
            print(f"... and {len(ticker_matches) - 10} more")
        
        print()
        
        # Strategy 3: Look for specific game matchups
        print("STRATEGY 3: Looking for 'Indianapolis' and 'Cincinnati' specifically...")
        specific_matches = []
        
        for market in all_markets_data:
            title = market.get('title', '').lower()
            
            if ('indianapolis' in title or 'colts' in title) and ('cincinnati' in title or 'bengals' in title):
                specific_matches.append(market)
        
        print(f"Found {len(specific_matches)} markets with Colts vs Bengals")
        for market in specific_matches:
            print(f"  {market.get('ticker')}: {market.get('title')}")
        
        print()
        
        # Strategy 4: Show some random titles to understand patterns
        print("STRATEGY 4: Sample of random market titles to understand patterns...")
        sample_markets = all_markets_data[1000:1020]  # Random sample
        for i, market in enumerate(sample_markets, 1):
            title = market.get('title', '')
            if len(title) < 80:  # Only show shorter titles
                print(f"{i:2d}. {market.get('ticker')}: {title}")
        
        print()
        print("ANALYSIS:")
        print("- Check if NFL games use different ticker patterns")  
        print("- See if team names appear differently in titles")
        print("- Determine if NFL games are even available on Kalshi currently")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    search_for_nfl_games()