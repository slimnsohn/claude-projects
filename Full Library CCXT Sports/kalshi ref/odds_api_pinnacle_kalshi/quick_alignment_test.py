"""
Quick Game Alignment Test
Tests if Pinnacle and Kalshi games now align with fixed dates
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

def main():
    """Quick alignment test"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\quick_alignment_test.py"
    print(f"Script: {script_path}")
    print()
    print("QUICK GAME ALIGNMENT TEST")
    print("=" * 40)
    
    try:
        from pinnacle_client import PinnacleClient
        from kalshi_client import KalshiClientUpdated as KalshiClient
        from data_aligner import GameMatcher
        
        print("1. Getting Pinnacle data...")
        pinnacle = PinnacleClient("keys/odds_api_key.txt")
        pinnacle_raw = pinnacle.get_sports_odds('mlb')
        
        if not pinnacle_raw.get('success'):
            print(f"   ERROR: {pinnacle_raw.get('error')}")
            return
        
        pinnacle_games = pinnacle.normalize_pinnacle_data(pinnacle_raw, 15)
        print(f"   Pinnacle games: {len(pinnacle_games)}")
        
        print("\n2. Getting Kalshi data...")
        kalshi = KalshiClient("keys/kalshi_credentials.txt")
        kalshi_raw = kalshi.search_sports_markets('mlb')
        
        if not kalshi_raw.get('success'):
            print(f"   ERROR: {kalshi_raw.get('error')}")
            return
        
        kalshi_games = kalshi.normalize_kalshi_data(kalshi_raw, 15)
        print(f"   Kalshi games: {len(kalshi_games)}")
        
        print("\n3. Sample data:")
        if pinnacle_games:
            p_game = pinnacle_games[0]
            print(f"   Pinnacle: {p_game['away_team']} @ {p_game['home_team']}")
            print(f"             Date: {p_game.get('game_date')}, Time: {p_game.get('game_time')}")
        
        if kalshi_games:
            k_game = kalshi_games[0]  
            print(f"   Kalshi:   {k_game['away_team']} @ {k_game['home_team']}")
            print(f"             Date: {k_game.get('game_date')}, Time: {k_game.get('game_time')}")
        
        print("\n4. Testing alignment...")
        matcher = GameMatcher(time_threshold_hours=6.0)
        aligned_games = matcher.align_games(pinnacle_games, kalshi_games)
        
        print(f"   Aligned games: {len(aligned_games)}")
        print(f"   Match rate: {len(aligned_games)/max(len(pinnacle_games),1)*100:.1f}%")
        
        if aligned_games:
            match = aligned_games[0]
            confidence = match['match_confidence']
            print(f"   Best match confidence: {confidence:.1%}")
            print("   SUCCESS: Games are aligning!")
        else:
            print("   WARNING: No games aligned")
            
            # Quick diagnosis
            print("\n   Quick diagnosis:")
            if len(pinnacle_games) == 0:
                print("   - No Pinnacle games available")
            elif len(kalshi_games) == 0:
                print("   - No Kalshi games available") 
            else:
                print("   - Games available but not matching")
                print("   - Could be team name differences")
                print("   - Could be time/date differences")
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 40)
    print("QUICK TEST COMPLETE")
    print(f"Script path: {script_path}")

if __name__ == "__main__":
    main()