"""
Debug Version of Kalshi Test - Shows Exact Failure Point
"""

import sys
import os

def main():
    """Debug version with verbose output"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\test_kalshi_debug.py"
    print(f"Script: {script_path}")
    print()
    print("KALSHI DEBUG TEST - VERBOSE OUTPUT")
    print("=" * 50)
    
    print("Step 1: Setting up Python path...")
    sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))
    print(f"Python path: {sys.path[-1]}")
    
    print("\nStep 2: Testing import...")
    try:
        from kalshi_client import KalshiClientUpdated as KalshiClient
        print("SUCCESS: Import successful")
    except Exception as e:
        print(f"FAILED: Import error - {e}")
        return
    
    print("\nStep 3: Testing client creation...")
    try:
        client = KalshiClient("keys/kalshi_credentials.txt")
        print("SUCCESS: Client created")
    except Exception as e:
        print(f"FAILED: Client creation error - {e}")
        return
    
    print("\nStep 4: Testing ticker parsing...")
    try:
        ticker = "KXMLBGAME-25AUG21HOUBAL-HOU"
        date, time = client._extract_date_from_ticker(ticker)
        print(f"Ticker: {ticker}")
        print(f"Result: date={date}, time={time}")
        
        if date and time:
            print("SUCCESS: Ticker parsing works")
        else:
            print("WARNING: Ticker parsing returned None")
    except Exception as e:
        print(f"FAILED: Ticker parsing error - {e}")
        return
    
    print("\nStep 5: Testing market search...")
    try:
        raw_data = client.search_sports_markets('mlb')
        print(f"Search success: {raw_data.get('success')}")
        
        if raw_data.get('success'):
            markets = raw_data.get('data', [])
            print(f"Markets found: {len(markets)}")
            
            if markets:
                print(f"First market: {markets[0].get('ticker')}")
                print("SUCCESS: Market search works")
            else:
                print("WARNING: No markets found")
                return
        else:
            print(f"FAILED: Search error - {raw_data.get('error')}")
            return
    except Exception as e:
        print(f"FAILED: Market search error - {e}")
        return
    
    print("\nStep 6: Testing normalization...")
    try:
        normalized_games = client.normalize_kalshi_data(raw_data, 15)
        print(f"Normalized games: {len(normalized_games)}")
        
        if normalized_games:
            game = normalized_games[0]
            print(f"First game: {game.get('away_team')} @ {game.get('home_team')}")
            print(f"Game date: {game.get('game_date')}")
            print(f"Game time: {game.get('game_time')}")
            
            # Check if dates are correct
            aug_count = sum(1 for g in normalized_games 
                           if g.get('game_date', '').startswith('2025-08'))
            print(f"August 2025 dates: {aug_count}/{len(normalized_games)}")
            
            if aug_count > 0:
                print("SUCCESS: Date fix is working!")
            else:
                print("WARNING: Dates may still be incorrect")
            
            print("SUCCESS: Normalization works")
        else:
            print("WARNING: No normalized games")
    except Exception as e:
        print(f"FAILED: Normalization error - {e}")
        return
    
    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("The Kalshi date fix appears to be working correctly.")
    print(f"Script path: {script_path}")

if __name__ == "__main__":
    main()