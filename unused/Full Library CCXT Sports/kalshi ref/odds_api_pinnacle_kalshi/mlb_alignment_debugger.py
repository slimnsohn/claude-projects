"""
MLB Alignment Debugger - Detailed Game Comparison
Shows exactly what's being compared between Pinnacle and Kalshi for MLB games
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

def show_detailed_comparison(pinnacle_games, kalshi_games):
    """Show detailed side-by-side comparison of all games"""
    print("DETAILED GAME COMPARISON")
    print("=" * 80)
    
    print(f"\nPINNACLE GAMES ({len(pinnacle_games)} total):")
    print("-" * 50)
    for i, game in enumerate(pinnacle_games):
        print(f"{i+1:2d}. Away: '{game['away_team']}' @ Home: '{game['home_team']}'")
        print(f"     Date: {game['game_date']} | Time: {game['game_time']}")
        print(f"     Sport: {game.get('sport', 'N/A')} | ID: {game.get('game_id', 'N/A')}")
        print()
    
    print(f"\nKALSHI GAMES ({len(kalshi_games)} total):")
    print("-" * 50)
    for i, game in enumerate(kalshi_games):
        print(f"{i+1:2d}. Away: '{game['away_team']}' @ Home: '{game['home_team']}'")
        print(f"     Date: {game['game_date']} | Time: {game['game_time']}")
        print(f"     Sport: {game.get('sport', 'N/A')} | ID: {game.get('game_id', 'N/A')}")
        print()

def analyze_team_matching(pinnacle_games, kalshi_games):
    """Analyze potential team name matches"""
    print("TEAM NAME MATCHING ANALYSIS")
    print("=" * 80)
    
    # Extract all unique team names
    pinnacle_teams = set()
    kalshi_teams = set()
    
    for game in pinnacle_games:
        pinnacle_teams.add(game['away_team'])
        pinnacle_teams.add(game['home_team'])
    
    for game in kalshi_games:
        kalshi_teams.add(game['away_team']) 
        kalshi_teams.add(game['home_team'])
    
    print(f"\nPINNACLE TEAMS ({len(pinnacle_teams)}):")
    for team in sorted(pinnacle_teams):
        print(f"  '{team}'")
    
    print(f"\nKALSHI TEAMS ({len(kalshi_teams)}):")
    for team in sorted(kalshi_teams):
        print(f"  '{team}'")
    
    # Check for potential matches
    print(f"\nPOTENTIAL TEAM MATCHES:")
    matches_found = 0
    for p_team in sorted(pinnacle_teams):
        for k_team in sorted(kalshi_teams):
            # Simple similarity check
            if p_team.upper() in k_team.upper() or k_team.upper() in p_team.upper():
                print(f"  '{p_team}' <-> '{k_team}'")
                matches_found += 1
            elif len(p_team) >= 3 and len(k_team) >= 3:
                # Check if abbreviation matches start of full name
                if p_team.upper() == k_team.upper()[:len(p_team)]:
                    print(f"  '{p_team}' <-> '{k_team}' (abbrev match)")
                    matches_found += 1
    
    if matches_found == 0:
        print("  No obvious team name matches found")
    else:
        print(f"  Found {matches_found} potential team matches")

def test_alignment_step_by_step(pinnacle_games, kalshi_games):
    """Test alignment process step by step"""
    print("STEP-BY-STEP ALIGNMENT TEST")
    print("=" * 80)
    
    from data_aligner import GameMatcher
    
    # Test with 10-minute threshold as requested
    matcher = GameMatcher(time_threshold_hours=10/60)  # 10 minutes in hours
    
    print(f"Testing with 10-minute time threshold...")
    
    for i, p_game in enumerate(pinnacle_games):
        print(f"\nTesting Pinnacle game {i+1}: {p_game['away_team']} @ {p_game['home_team']}")
        print(f"  Date: {p_game['game_date']}, Time: {p_game['game_time']}")
        
        best_match = None
        best_confidence = 0.0
        
        for j, k_game in enumerate(kalshi_games):
            confidence = matcher._calculate_match_confidence(p_game, k_game)
            
            if confidence > 0.1:  # Show any reasonable confidence
                print(f"    vs Kalshi {j+1}: {k_game['away_team']} @ {k_game['home_team']} -> {confidence:.1%}")
                if confidence > best_confidence:
                    best_match = k_game
                    best_confidence = confidence
        
        if best_match:
            print(f"    BEST MATCH: {best_confidence:.1%} confidence")
            if best_confidence >= 0.7:
                print(f"    WOULD ALIGN: {best_confidence:.1%} >= 70% threshold")
            else:
                print(f"    TOO LOW: {best_confidence:.1%} < 70% threshold")
        else:
            print(f"    NO VIABLE MATCHES")

def main():
    """Main debugger function"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\mlb_alignment_debugger.py"
    print(f"Script: {script_path}")
    print()
    print("MLB ALIGNMENT DEBUGGER")
    print("Detailed analysis of why games aren't aligning")
    print("=" * 80)
    
    try:
        from pinnacle_client import PinnacleClient
        from kalshi_client import KalshiClientUpdated as KalshiClient
        
        print("Step 1: Fetching MLB data from both platforms...")
        
        # Get data
        pinnacle = PinnacleClient("keys/odds_api_key.txt")
        kalshi = KalshiClient("keys/kalshi_credentials.txt")
        
        pinnacle_raw = pinnacle.get_sports_odds('mlb')
        kalshi_raw = kalshi.search_sports_markets('mlb')
        
        if not pinnacle_raw.get('success'):
            print(f"ERROR: Pinnacle failed - {pinnacle_raw.get('error')}")
            return
        if not kalshi_raw.get('success'):
            print(f"ERROR: Kalshi failed - {kalshi_raw.get('error')}")
            return
        
        # Normalize data
        pinnacle_games = pinnacle.normalize_pinnacle_data(pinnacle_raw, 15)
        kalshi_games = kalshi.normalize_kalshi_data(kalshi_raw, 15)
        
        print(f"  Pinnacle: {len(pinnacle_games)} future games")
        print(f"  Kalshi: {len(kalshi_games)} future games")
        
        if not pinnacle_games:
            print("ERROR: No Pinnacle games available")
            return
        if not kalshi_games:
            print("ERROR: No Kalshi games available") 
            return
        
        # Show detailed comparison
        show_detailed_comparison(pinnacle_games, kalshi_games)
        
        # Analyze team matching
        analyze_team_matching(pinnacle_games, kalshi_games)
        
        # Test alignment step by step
        test_alignment_step_by_step(pinnacle_games, kalshi_games)
        
        print(f"\n" + "=" * 80)
        print("FINAL ALIGNMENT TEST WITH 10-MINUTE THRESHOLD")
        print("=" * 80)
        
        from data_aligner import GameMatcher
        matcher = GameMatcher(time_threshold_hours=10/60)  # 10 minutes
        aligned_games = matcher.align_games(pinnacle_games, kalshi_games)
        
        print(f"Final result: {len(aligned_games)} games aligned with 10-minute threshold")
        
        if aligned_games:
            print("\nSUCCESS: Games are aligning!")
            for i, match in enumerate(aligned_games):
                conf = match['match_confidence']
                p_game = match['pinnacle_data']
                k_game = match['kalshi_data']
                print(f"\nMatch {i+1} (Confidence: {conf:.1%}):")
                print(f"  Pinnacle: {p_game['away_team']} @ {p_game['home_team']}")
                print(f"  Kalshi:   {k_game['away_team']} @ {k_game['home_team']}")
        else:
            print("\nNO ALIGNMENT: Need to investigate further...")
            print("Possible issues:")
            print("1. Different team name formats (check team matching analysis above)")
            print("2. Date differences (check dates in detailed comparison above)")
            print("3. Confidence threshold too high (70% minimum)")
            print("4. Time differences > 10 minutes")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nScript path: {script_path}")

if __name__ == "__main__":
    main()