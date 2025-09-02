"""
Find Alignment Opportunities - Focused Analysis
Shows normalized odds view and identifies alignment issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

def main():
    """Focus on finding alignable games"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\find_alignment_opportunities.py"
    print(f"Script: {script_path}")
    print()
    print("ALIGNMENT OPPORTUNITY FINDER")
    print("=" * 60)
    
    try:
        from pinnacle_client import PinnacleClient
        from kalshi_client import KalshiClientUpdated as KalshiClient
        from data_aligner import GameMatcher
        
        # Get data from both platforms
        print("Step 1: Fetching data from both platforms...")
        pinnacle = PinnacleClient("keys/odds_api_key.txt")
        kalshi = KalshiClient("keys/kalshi_credentials.txt")
        
        # Fetch raw data
        pinnacle_raw = pinnacle.get_sports_odds('mlb')
        kalshi_raw = kalshi.search_sports_markets('mlb')
        
        if not pinnacle_raw.get('success'):
            print(f"   ERROR: Pinnacle failed - {pinnacle_raw.get('error')}")
            return
        if not kalshi_raw.get('success'):
            print(f"   ERROR: Kalshi failed - {kalshi_raw.get('error')}")
            return
        
        # Normalize data
        pinnacle_games = pinnacle.normalize_pinnacle_data(pinnacle_raw, 15)
        kalshi_games = kalshi.normalize_kalshi_data(kalshi_raw, 15)
        
        print(f"   Pinnacle: {len(pinnacle_games)} future games")
        print(f"   Kalshi: {len(kalshi_games)} future games")
        
        if not pinnacle_games or not kalshi_games:
            print("   ERROR: No games available for alignment")
            return
        
        print(f"\nStep 2: Normalized Odds View")
        print("-" * 40)
        
        # Show Pinnacle games with normalized odds
        print("PINNACLE GAMES:")
        for i, game in enumerate(pinnacle_games[:5]):  # Show first 5
            home_prob = game['home_odds']['implied_probability']
            away_prob = game['away_odds']['implied_probability']
            print(f"  {i+1}. {game['away_team']} @ {game['home_team']}")
            print(f"      Date: {game['game_date']}, Time: {game['game_time']}")
            print(f"      Home: {home_prob:.1%} | Away: {away_prob:.1%}")
        
        print(f"\nKALSHI GAMES:")
        for i, game in enumerate(kalshi_games[:5]):  # Show first 5
            home_prob = game['home_odds']['implied_probability']
            away_prob = game['away_odds']['implied_probability']
            print(f"  {i+1}. {game['away_team']} @ {game['home_team']}")
            print(f"      Date: {game['game_date']}, Time: {game['game_time']}")
            print(f"      Home: {home_prob:.1%} | Away: {away_prob:.1%}")
        
        print(f"\nStep 3: Detailed Alignment Analysis")
        print("-" * 40)
        
        # Collect all unique dates
        pinnacle_dates = set(g['game_date'] for g in pinnacle_games)
        kalshi_dates = set(g['game_date'] for g in kalshi_games)
        common_dates = pinnacle_dates & kalshi_dates
        
        print(f"Pinnacle dates: {sorted(pinnacle_dates)}")
        print(f"Kalshi dates: {sorted(kalshi_dates)}")
        print(f"Common dates: {sorted(common_dates)}")
        
        if not common_dates:
            print("\nNO COMMON DATES - Main alignment issue identified!")
            print("Need games on same dates to align properly.")
        else:
            print(f"\nFound {len(common_dates)} common date(s) - Good alignment potential!")
            
            # Show games on common dates
            for date in sorted(common_dates):
                print(f"\nGames on {date}:")
                
                pinnacle_date_games = [g for g in pinnacle_games if g['game_date'] == date]
                kalshi_date_games = [g for g in kalshi_games if g['game_date'] == date]
                
                pinnacle_matchups = [f"{g['away_team']}@{g['home_team']}" for g in pinnacle_date_games]
                kalshi_matchups = [f"{g['away_team']}@{g['home_team']}" for g in kalshi_date_games]
                print(f"  Pinnacle ({len(pinnacle_date_games)}): {pinnacle_matchups}")
                print(f"  Kalshi ({len(kalshi_date_games)}): {kalshi_matchups}")
        
        print(f"\nStep 4: Testing Alignment with Relaxed Criteria")
        print("-" * 40)
        
        # Try alignment with relaxed time threshold
        matcher = GameMatcher(time_threshold_hours=24.0)  # Very relaxed
        aligned_games = matcher.align_games(pinnacle_games, kalshi_games)
        
        print(f"Aligned with 24-hour threshold: {len(aligned_games)} games")
        
        if aligned_games:
            print("\nSUCCESS: Found alignable games!")
            for i, match in enumerate(aligned_games[:3]):  # Show first 3
                conf = match['match_confidence']
                p_game = match['pinnacle_data']
                k_game = match['kalshi_data']
                
                print(f"\nMatch {i+1} (Confidence: {conf:.1%}):")
                print(f"  Pinnacle: {p_game['away_team']} @ {p_game['home_team']} on {p_game['game_date']}")
                print(f"  Kalshi:   {k_game['away_team']} @ {k_game['home_team']} on {k_game['game_date']}")
                
                # Show odds comparison
                p_home = p_game['home_odds']['implied_probability']
                p_away = p_game['away_odds']['implied_probability']
                k_home = k_game['home_odds']['implied_probability']
                k_away = k_game['away_odds']['implied_probability']
                
                print(f"  Home odds: Pinnacle {p_home:.1%} vs Kalshi {k_home:.1%} (diff: {abs(p_home-k_home):.1%})")
                print(f"  Away odds: Pinnacle {p_away:.1%} vs Kalshi {k_away:.1%} (diff: {abs(p_away-k_away):.1%})")
                
                # Check for significant edge
                max_diff = max(abs(p_home-k_home), abs(p_away-k_away))
                if max_diff >= 0.05:  # 5% edge
                    print(f"  OPPORTUNITY: {max_diff:.1%} edge detected!")
        else:
            print("No games aligned even with relaxed criteria.")
            print("\nDiagnosing alignment issues...")
            
            # Sample team name comparison
            if pinnacle_games and kalshi_games:
                p_sample = pinnacle_games[0]
                k_sample = kalshi_games[0]
                print(f"\nSample team formats:")
                print(f"  Pinnacle: '{p_sample['away_team']}' @ '{p_sample['home_team']}'")
                print(f"  Kalshi:   '{k_sample['away_team']}' @ '{k_sample['home_team']}'")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 60)
    print("ALIGNMENT ANALYSIS COMPLETE")
    print(f"Script path: {script_path}")

if __name__ == "__main__":
    main()