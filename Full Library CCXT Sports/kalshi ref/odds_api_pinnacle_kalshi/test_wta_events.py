"""
Test WTA Tennis Events
Test if both Pinnacle and Kalshi have WTA tennis events available
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

def main():
    """Test WTA tennis events on both platforms"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\test_wta_events.py"
    print(f"Script: {script_path}")
    print()
    print("WTA TENNIS EVENTS TEST")
    print("Testing both Pinnacle and Kalshi for tennis/WTA")
    print("=" * 60)
    
    try:
        from pinnacle_client import PinnacleClient
        from kalshi_client import KalshiClientUpdated as KalshiClient
        
        # Test Pinnacle WTA events
        print("TESTING PINNACLE WTA EVENTS:")
        print("-" * 40)
        pinnacle = PinnacleClient('keys/odds_api_key.txt')
        pinnacle_result = pinnacle.get_sports_odds('tennis')
        
        if pinnacle_result.get('success'):
            games = pinnacle_result.get('data', [])
            print(f"SUCCESS: Found {len(games)} tennis events on Pinnacle")
            
            # Show first few games
            for i, game in enumerate(games[:3]):
                home_team = game.get('home_team', 'Unknown')
                away_team = game.get('away_team', 'Unknown')
                start_time = game.get('commence_time', 'Unknown')
                # Handle special characters in player names
                try:
                    print(f"  Game {i+1}: {away_team} vs {home_team} at {start_time}")
                except UnicodeEncodeError:
                    home_clean = home_team.encode('ascii', 'replace').decode('ascii')
                    away_clean = away_team.encode('ascii', 'replace').decode('ascii')
                    print(f"  Game {i+1}: {away_clean} vs {home_clean} at {start_time}")
        else:
            print(f"FAILED: {pinnacle_result.get('error', 'Unknown error')}")
        
        print()
        
        # Test Kalshi WTA events
        print("TESTING KALSHI WTA EVENTS:")
        print("-" * 40)
        kalshi = KalshiClient('keys/kalshi_credentials.txt')
        kalshi_result = kalshi.search_sports_markets('tennis')
        
        if kalshi_result.get('success'):
            markets = kalshi_result.get('data', [])
            print(f"SUCCESS: Found {len(markets)} tennis markets on Kalshi")
            
            # Show first few markets
            for i, market in enumerate(markets[:3]):
                title = market.get('title', 'Unknown')
                ticker = market.get('ticker', 'Unknown')
                yes_sub_title = market.get('yes_sub_title', 'Unknown')
                # Handle special characters
                try:
                    print(f"  Market {i+1}: {title}")
                    print(f"    Ticker: {ticker}")
                    print(f"    YES for: {yes_sub_title}")
                except UnicodeEncodeError:
                    title_clean = title.encode('ascii', 'replace').decode('ascii')
                    yes_clean = yes_sub_title.encode('ascii', 'replace').decode('ascii')
                    print(f"  Market {i+1}: {title_clean}")
                    print(f"    Ticker: {ticker}")
                    print(f"    YES for: {yes_clean}")
                print()
        else:
            print(f"FAILED: {kalshi_result.get('error', 'Unknown error')}")
        
        print()
        
        # Test complete system integration
        print("TESTING SYSTEM INTEGRATION:")
        print("-" * 40)
        
        if pinnacle_result.get('success') and kalshi_result.get('success'):
            pinnacle_count = len(pinnacle_result.get('data', []))
            kalshi_count = len(kalshi_result.get('data', []))
            
            if pinnacle_count > 0 and kalshi_count > 0:
                print("SUCCESS: Both platforms have tennis events")
                print(f"  Pinnacle: {pinnacle_count} events")
                print(f"  Kalshi: {kalshi_count} markets")
                print("  Ready for alignment testing")
            else:
                print("WARNING: One or both platforms have no tennis events")
                print(f"  Pinnacle: {pinnacle_count} events")
                print(f"  Kalshi: {kalshi_count} markets")
        else:
            print("ERROR: Cannot test integration - one or both platforms failed")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\\nScript path: {script_path}")

if __name__ == "__main__":
    main()