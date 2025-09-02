"""
Simple Test for Kalshi Date Fix (No Unicode)
Tests that game dates are correctly extracted from tickers
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

from kalshi_client import KalshiClientUpdated as KalshiClient

def main():
    """Simple test of the Kalshi date fix"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\test_kalshi_dates_simple.py"
    print(f"Script: {script_path}")
    print()
    print("KALSHI DATE FIX TEST")
    print("=" * 50)
    
    try:
        client = KalshiClient("keys/kalshi_credentials.txt")
        
        # Test ticker parsing directly
        print("1. TICKER PARSING TEST:")
        test_tickers = [
            "KXMLBGAME-25AUG21HOUBAL-HOU",
            "KXMLBGAME-25AUG21ATHMIN-MIN"
        ]
        
        for ticker in test_tickers:
            date, time = client._extract_date_from_ticker(ticker)
            print(f"   {ticker}")
            print(f"   -> Date: {date}, Time: {time}")
        print()
        
        # Test with real data
        print("2. REAL DATA TEST:")
        raw_data = client.search_sports_markets('mlb')
        
        if raw_data.get('success'):
            markets = raw_data.get('data', [])
            normalized_games = client.normalize_kalshi_data(raw_data, 15)
            
            print(f"   Raw markets: {len(markets)}")
            print(f"   Normalized games: {len(normalized_games)}")
            
            # Show first few games
            print("   First 3 games:")
            for i, game in enumerate(normalized_games[:3], 1):
                print(f"     {i}. {game['away_team']} @ {game['home_team']}")
                print(f"        Date: {game.get('game_date', 'N/A')}")
                print(f"        Time: {game.get('game_time', 'N/A')}")
            
            # Count correct dates
            aug_2025_count = sum(1 for game in normalized_games 
                                if game.get('game_date', '').startswith('2025-08'))
            
            print(f"   Games with August 2025 dates: {aug_2025_count}/{len(normalized_games)}")
            
            if aug_2025_count > 0:
                print("   SUCCESS: Date fix is working!")
            else:
                print("   ERROR: Dates still incorrect")
        else:
            print(f"   ERROR: {raw_data.get('error')}")
    
    except Exception as e:
        print(f"ERROR: {e}")
    
    print()
    print("=" * 50)
    print("TEST COMPLETE")
    print(f"Script path: {script_path}")

if __name__ == "__main__":
    main()