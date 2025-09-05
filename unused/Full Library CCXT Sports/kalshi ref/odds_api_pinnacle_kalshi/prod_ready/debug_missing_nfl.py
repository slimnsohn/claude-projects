#!/usr/bin/env python3
"""
Debug why we're missing NFL games that actually exist
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.kalshi_client import KalshiClientUpdated as KalshiClient

def debug_missing_nfl_games():
    """Debug why we can't find NFL games that actually exist"""
    
    print("DEBUGGING MISSING NFL GAMES")
    print("=" * 60)
    print("Looking for: KXNFLGAME-25AUG23INDCIN (Indianapolis vs Cincinnati)")
    print()
    
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        creds_path = os.path.join(project_root, 'keys', 'kalshi_credentials.txt')
        client = KalshiClient(creds_path)
        
        # Test 1: Get all markets and search for NFL specifically
        print("TEST 1: Searching all markets for KXNFLGAME...")
        all_markets = client._get_all_markets_paginated()
        all_markets_data = all_markets.get('data', [])
        
        nfl_markets = []
        indcin_markets = []
        
        for market in all_markets_data:
            ticker = market.get('ticker', '')
            title = market.get('title', '')
            
            # Look for KXNFLGAME specifically
            if 'KXNFLGAME' in ticker.upper():
                nfl_markets.append(market)
                print(f"FOUND NFL: {ticker} - {title}")
            
            # Look for Indianapolis/Cincinnati specifically
            if ('indianapolis' in title.lower() or 'colts' in title.lower() or 'ind' in ticker.upper()) and \
               ('cincinnati' in title.lower() or 'bengals' in title.lower() or 'cin' in ticker.upper()):
                indcin_markets.append(market)
                print(f"FOUND IND/CIN: {ticker} - {title}")
        
        print(f"\nTotal NFL markets found: {len(nfl_markets)}")
        print(f"Total Indy/Cincy markets found: {len(indcin_markets)}")
        
        # Test 2: Try the specific ticker search
        print("\nTEST 2: Looking for the exact ticker...")
        exact_ticker = "KXNFLGAME-25AUG23INDCIN"
        
        found_exact = None
        for market in all_markets_data:
            if market.get('ticker') == exact_ticker:
                found_exact = market
                break
        
        if found_exact:
            print(f"SUCCESS: Found exact ticker!")
            print(f"  Ticker: {found_exact.get('ticker')}")
            print(f"  Title: {found_exact.get('title')}")
            print(f"  Status: {found_exact.get('status')}")
            print(f"  Close Time: {found_exact.get('close_time')}")
        else:
            print(f"NOT FOUND: {exact_ticker} not in our market data")
        
        # Test 3: Check if pagination is working properly
        print(f"\nTEST 3: Pagination check...")
        print(f"Total markets retrieved: {len(all_markets_data)}")
        print(f"Expected: Should be getting all available markets")
        
        # Test 4: Look for any game-like tickers with today's date
        print(f"\nTEST 4: Looking for games with today's date (AUG23)...")
        aug23_games = []
        
        for market in all_markets_data:
            ticker = market.get('ticker', '')
            if 'AUG23' in ticker.upper() and 'GAME' in ticker.upper():
                aug23_games.append(market)
        
        print(f"Found {len(aug23_games)} games with AUG23 date:")
        for market in aug23_games:
            print(f"  {market.get('ticker')} - {market.get('title')}")
        
        # Test 5: Test the sport-specific search method
        print(f"\nTEST 5: Testing sport-specific search method...")
        nfl_search_result = client.search_sports_markets('nfl')
        
        if nfl_search_result.get('success'):
            nfl_data = nfl_search_result.get('data', [])
            print(f"Sport-specific search found {len(nfl_data)} NFL markets")
            for market in nfl_data[:5]:  # Show first 5
                print(f"  {market.get('ticker')} - {market.get('title')}")
        else:
            print(f"Sport-specific search failed: {nfl_search_result.get('error')}")
        
        print("\nDIAGNOSIS:")
        print("- Check if market exists in our data")
        print("- Verify pagination is getting all markets")
        print("- Test if search filtering is too restrictive")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_missing_nfl_games()