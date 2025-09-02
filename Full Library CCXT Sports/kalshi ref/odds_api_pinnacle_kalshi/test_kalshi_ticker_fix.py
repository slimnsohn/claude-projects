"""
Test Kalshi Ticker Date Extraction Fix
Verifies that game dates are now correctly extracted from tickers
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

from kalshi_client import KalshiClientUpdated as KalshiClient

def test_ticker_date_extraction():
    """Test the new ticker date extraction method"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\test_kalshi_ticker_fix.py"
    print(f"Script: {script_path}")
    print()
    print("=" * 80)
    print("TESTING KALSHI TICKER DATE EXTRACTION FIX")
    print("=" * 80)
    
    try:
        client = KalshiClient("keys/kalshi_credentials.txt")
        
        # Test the extraction method directly
        test_tickers = [
            "KXMLBGAME-25AUG21HOUBAL-HOU",
            "KXMLBGAME-25AUG21ATHMIN-MIN", 
            "KXNFLGAME-08SEP24BUFMIA-BUF",
            "KXNBAGAME-15NOV24LALGAME-LAL",
            "invalid-ticker",
            "KXMLB-NOTICKER",
            ""
        ]
        
        print("TICKER DATE EXTRACTION TESTS:")
        print("-" * 50)
        
        for ticker in test_tickers:
            date, time = client._extract_date_from_ticker(ticker)
            status = "SUCCESS" if date and time else "FAILED"
            print(f"{status} {ticker}")
            print(f"    → Date: {date or 'None'}")
            print(f"    → Time: {time or 'None'}")
            print()
        
        # Test with real market data
        print("REAL MARKET DATA TEST:")
        print("-" * 50)
        
        raw_data = client.search_sports_markets('mlb')
        if raw_data.get('success'):
            markets = raw_data.get('data', [])[:5]
            
            for i, market in enumerate(markets, 1):
                ticker = market.get('ticker')
                title = market.get('title')
                close_time = market.get('close_time')
                
                # Test extraction
                date, time = client._extract_date_from_ticker(ticker)
                
                print(f"{i}. {ticker}")
                print(f"   Title: {title}")
                print(f"   Close time: {close_time}")
                print(f"   → Extracted date: {date}")
                print(f"   → Extracted time: {time}")
                
                if date:
                    from datetime import datetime
                    try:
                        parsed_date = datetime.strptime(date, '%Y-%m-%d')
                        print(f"   Validates as: {parsed_date.strftime('%B %d, %Y')}")
                    except:
                        print(f"  Invalid date format")
                else:
                    print(f"  No date extracted")
                print()
        
    except Exception as e:
        print(f"ERROR: {e}")

def test_normalized_data_with_fix():
    """Test normalized data with the ticker date fix"""
    print("=" * 80)
    print("TESTING NORMALIZED DATA WITH TICKER DATE FIX")
    print("=" * 80)
    
    try:
        client = KalshiClient("keys/kalshi_credentials.txt")
        
        # Get raw data
        raw_data = client.search_sports_markets('mlb')
        if not raw_data.get('success'):
            print(f"Raw data error: {raw_data.get('error')}")
            return
        
        # Get normalized data with the fix
        normalized_games = client.normalize_kalshi_data(raw_data, 15)
        
        print(f"Raw markets: {len(raw_data.get('data', []))}")
        print(f"Normalized games: {len(normalized_games)}")
        print()
        
        print("NORMALIZED GAME DATA (first 5):")
        print("-" * 60)
        
        for i, game in enumerate(normalized_games[:5], 1):
            print(f"{i}. {game['away_team']} @ {game['home_team']}")
            print(f"   Game date: {game.get('game_date', 'N/A')}")
            print(f"   Game time: {game.get('game_time', 'N/A')}")
            print(f"   Display: {game.get('game_time_display', 'N/A')}")
            print(f"   Sport: {game.get('sport', 'N/A')}")
            
            # Show metadata
            metadata = game.get('metadata', {})
            original_close = metadata.get('original_close_time', 'N/A')
            ticker_date = metadata.get('ticker_parsed_date', 'N/A')
            
            print(f"   Original close: {original_close}")
            print(f"   Ticker date: {ticker_date}")
            print()
        
        # Check if dates are now correct
        correct_dates = 0
        for game in normalized_games:
            game_date = game.get('game_date', '')
            if game_date.startswith('2025-08'):  # August 2025
                correct_dates += 1
        
        print(f" RESULTS:")
        print(f"   Games with August 2025 dates: {correct_dates}/{len(normalized_games)}")
        if correct_dates > 0:
            print(f"   Fix appears to be working!")
        else:
            print(f"    Still seeing incorrect dates")
        
    except Exception as e:
        print(f"ERROR: {e}")

def compare_before_after_fix():
    """Show comparison of old vs new date extraction"""
    print("=" * 80)
    print("BEFORE/AFTER COMPARISON")
    print("=" * 80)
    
    try:
        client = KalshiClient("keys/kalshi_credentials.txt")
        raw_data = client.search_sports_markets('mlb')
        
        if not raw_data.get('success'):
            print(f" Error: {raw_data.get('error')}")
            return
        
        markets = raw_data.get('data', [])[:3]
        
        print("OLD vs NEW DATE EXTRACTION:")
        print("-" * 50)
        
        for i, market in enumerate(markets, 1):
            ticker = market.get('ticker', 'N/A')
            close_time = market.get('close_time', 'N/A')
            
            # Old way: use close_time
            old_date = close_time[:10] if close_time else None
            
            # New way: extract from ticker
            new_date, new_time = client._extract_date_from_ticker(ticker)
            
            print(f"{i}. {ticker}")
            print(f"   OLD (close_time): {old_date}")
            print(f"   NEW (ticker):     {new_date}")
            
            if new_date and old_date:
                if new_date != old_date:
                    print(f"   FIXED: {old_date} → {new_date}")
                else:
                    print(f"     Same date")
            elif new_date:
                print(f"   NEW method found date")
            else:
                print(f"   NEW method failed")
            print()
    
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    """Main test function"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\test_kalshi_ticker_fix.py"
    
    print("KALSHI TICKER DATE FIX VERIFICATION")
    print("Testing extraction of game dates from ticker format")
    print("Example: KXMLBGAME-25AUG21HOUBAL-HOU → 2025-08-25")
    print()
    
    # Test 1: Direct ticker extraction
    test_ticker_date_extraction()
    
    # Test 2: Normalized data with fix
    test_normalized_data_with_fix()
    
    # Test 3: Before/after comparison
    compare_before_after_fix()
    
    print("=" * 80)
    print("KALSHI TICKER FIX TEST COMPLETE")
    print("=" * 80)
    print()
    print("EXPECTED RESULTS:")
    print(" Dates should now show August 2025 (not September)")
    print(" Game times estimated as 19:00 (7 PM)")
    print(" Ticker parsing should extract correct dates")
    print()
    print(f"Script path: {script_path}")

if __name__ == "__main__":
    main()