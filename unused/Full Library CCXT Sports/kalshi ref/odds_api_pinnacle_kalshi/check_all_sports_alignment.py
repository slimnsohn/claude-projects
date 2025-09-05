"""
Check All Sports for Alignment Opportunities
Test multiple sports to find alignable games
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

def check_sport_alignment(sport_name):
    """Check alignment for a specific sport"""
    print(f"\n=== {sport_name.upper()} ALIGNMENT CHECK ===")
    
    try:
        from pinnacle_client import PinnacleClient
        from kalshi_client import KalshiClientUpdated as KalshiClient
        from data_aligner import GameMatcher
        
        pinnacle = PinnacleClient("keys/odds_api_key.txt")
        kalshi = KalshiClient("keys/kalshi_credentials.txt")
        
        # Get data
        pinnacle_raw = pinnacle.get_sports_odds(sport_name)
        kalshi_raw = kalshi.search_sports_markets(sport_name)
        
        if not pinnacle_raw.get('success') or not kalshi_raw.get('success'):
            print(f"  Data fetch failed for {sport_name}")
            return 0
        
        # Normalize
        pinnacle_games = pinnacle.normalize_pinnacle_data(pinnacle_raw, 15)
        kalshi_games = kalshi.normalize_kalshi_data(kalshi_raw, 15)
        
        print(f"  Pinnacle: {len(pinnacle_games)} games")
        print(f"  Kalshi: {len(kalshi_games)} games")
        
        if not pinnacle_games or not kalshi_games:
            print(f"  No games available for {sport_name}")
            return 0
        
        # Check dates
        pinnacle_dates = set(g['game_date'] for g in pinnacle_games)
        kalshi_dates = set(g['game_date'] for g in kalshi_games)
        common_dates = pinnacle_dates & kalshi_dates
        
        print(f"  Common dates: {len(common_dates)} ({sorted(common_dates) if common_dates else 'None'})")
        
        if common_dates:
            # Try alignment
            matcher = GameMatcher(time_threshold_hours=6.0)
            aligned_games = matcher.align_games(pinnacle_games, kalshi_games)
            print(f"  Aligned games: {len(aligned_games)}")
            
            if aligned_games:
                match = aligned_games[0]
                conf = match['match_confidence']
                print(f"  Best match confidence: {conf:.1%}")
                return len(aligned_games)
        
        return 0
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return 0

def main():
    """Check multiple sports for alignment opportunities"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\check_all_sports_alignment.py"
    print(f"Script: {script_path}")
    print()
    print("MULTI-SPORT ALIGNMENT CHECKER")
    print("=" * 50)
    
    sports_to_check = ['mlb', 'nfl', 'nba', 'nhl']
    total_aligned = 0
    
    for sport in sports_to_check:
        aligned_count = check_sport_alignment(sport)
        total_aligned += aligned_count
    
    print(f"\n" + "=" * 50)
    print("MULTI-SPORT SUMMARY")
    print(f"Total aligned games across all sports: {total_aligned}")
    
    if total_aligned > 0:
        print("SUCCESS: Found alignable games!")
        print("The system can detect mispricing opportunities.")
    else:
        print("No aligned games found across any sport.")
        print("Possible reasons:")
        print("1. Different game scheduling (dates don't overlap)")
        print("2. Team name matching issues")
        print("3. Time threshold too strict")
    
    print(f"\nScript path: {script_path}")

if __name__ == "__main__":
    main()