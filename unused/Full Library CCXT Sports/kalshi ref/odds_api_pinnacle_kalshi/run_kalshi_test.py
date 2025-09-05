"""
Direct Python Script - Kalshi Date Fix Test
Run this directly with: python run_kalshi_test.py
"""

import sys
import os

def main():
    """Main function - runs directly without pytest"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\run_kalshi_test.py"
    print(f"Script: {script_path}")
    print()
    
    print("KALSHI DATE FIX TEST")
    print("=" * 50)
    print("Running direct Python script (not pytest)")
    print()
    
    # Setup path
    print("Setting up Python path...")
    sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))
    print("Done.")
    
    # Import and test
    try:
        print("\nImporting Kalshi client...")
        from kalshi_client import KalshiClientUpdated as KalshiClient
        print("Success.")
        
        print("\nCreating client...")
        client = KalshiClient("keys/kalshi_credentials.txt")
        print("Success.")
        
        print("\nTesting ticker parsing...")
        test_ticker = "KXMLBGAME-25AUG21HOUBAL-HOU"
        date, time = client._extract_date_from_ticker(test_ticker)
        print(f"Ticker: {test_ticker}")
        print(f"Result: date={date}, time={time}")
        
        if date == "2025-08-25" and time == "19:00":
            print("SUCCESS: Ticker parsing is correct!")
        else:
            print("ERROR: Ticker parsing failed")
            return
        
        print("\nTesting market search...")
        raw_data = client.search_sports_markets('mlb')
        
        if raw_data.get('success'):
            markets = raw_data.get('data', [])
            print(f"Found {len(markets)} markets")
            
            if markets:
                print(f"First market: {markets[0].get('ticker')}")
                
                print("\nTesting normalization...")
                normalized_games = client.normalize_kalshi_data(raw_data, 15)
                print(f"Normalized {len(normalized_games)} games")
                
                if normalized_games:
                    # Check dates
                    aug_count = 0
                    for game in normalized_games:
                        if game.get('game_date', '').startswith('2025-08'):
                            aug_count += 1
                    
                    print(f"Games with August 2025 dates: {aug_count}/{len(normalized_games)}")
                    
                    # Show sample
                    sample = normalized_games[0]
                    print(f"Sample game: {sample.get('away_team')} @ {sample.get('home_team')}")
                    print(f"Date: {sample.get('game_date')}, Time: {sample.get('game_time')}")
                    
                    if aug_count > 0:
                        print("\nSUCCESS: Date fix is working correctly!")
                        print("Games now show August 2025 dates instead of September settlement dates.")
                    else:
                        print("\nWARNING: No August dates found.")
                        # Show what dates we have
                        dates = set(g.get('game_date') for g in normalized_games if g.get('game_date'))
                        print(f"Dates found: {sorted(dates)}")
                else:
                    print("No games after normalization")
            else:
                print("No markets found")
        else:
            print(f"Market search failed: {raw_data.get('error')}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print()
    print("To run as pytest instead:")
    print("pytest test_kalshi_pytest.py -v")
    print()
    print(f"Script path: {script_path}")

if __name__ == "__main__":
    main()