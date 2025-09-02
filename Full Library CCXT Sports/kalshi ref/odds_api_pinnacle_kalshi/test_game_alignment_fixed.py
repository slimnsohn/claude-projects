"""
Test Game Alignment with Fixed Kalshi Dates
Verifies that games now align properly between Pinnacle and Kalshi
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

from pinnacle_client import PinnacleClient
from kalshi_client import KalshiClientUpdated as KalshiClient
from data_aligner import GameMatcher

def test_alignment_with_fixed_dates(sport='mlb'):
    """Test game alignment with the fixed Kalshi dates"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\test_game_alignment_fixed.py"
    print(f"Script: {script_path}")
    print()
    print("GAME ALIGNMENT TEST WITH FIXED DATES")
    print("=" * 60)
    
    try:
        # Get data from both platforms
        print("1. FETCHING DATA FROM BOTH PLATFORMS")
        print("-" * 40)
        
        pinnacle = PinnacleClient("keys/odds_api_key.txt")
        kalshi = KalshiClient("keys/kalshi_credentials.txt")
        
        # Get Pinnacle data
        pinnacle_raw = pinnacle.get_sports_odds(sport)
        if not pinnacle_raw.get('success'):
            print(f"ERROR: Pinnacle failed - {pinnacle_raw.get('error')}")
            return
        
        pinnacle_games = pinnacle.normalize_pinnacle_data(pinnacle_raw, 15)
        print(f"Pinnacle games: {len(pinnacle_games)}")
        
        # Get Kalshi data (with fixed dates)
        kalshi_raw = kalshi.search_sports_markets(sport)
        if not kalshi_raw.get('success'):
            print(f"ERROR: Kalshi failed - {kalshi_raw.get('error')}")
            return
        
        kalshi_games = kalshi.normalize_kalshi_data(kalshi_raw, 15)
        print(f"Kalshi games: {len(kalshi_games)}")
        print()
        
        # Show sample data from each platform
        print("2. SAMPLE DATA COMPARISON")
        print("-" * 40)
        
        print("PINNACLE GAMES (first 3):")
        for i, game in enumerate(pinnacle_games[:3], 1):
            print(f"  {i}. {game['away_team']} @ {game['home_team']}")
            print(f"     Date: {game.get('game_date', 'N/A')}")
            print(f"     Time: {game.get('game_time_display', 'N/A')}")
        print()
        
        print("KALSHI GAMES (first 3):")
        for i, game in enumerate(kalshi_games[:3], 1):
            print(f"  {i}. {game['away_team']} @ {game['home_team']}")
            print(f"     Date: {game.get('game_date', 'N/A')}")
            print(f"     Time: {game.get('game_time_display', 'N/A')}")
        print()
        
        # Test alignment
        print("3. TESTING GAME ALIGNMENT")
        print("-" * 40)
        
        matcher = GameMatcher(time_threshold_hours=6.0)  # Allow 6 hour difference
        aligned_games = matcher.align_games(pinnacle_games, kalshi_games)
        
        print(f"Alignment results:")
        print(f"  Pinnacle games: {len(pinnacle_games)}")
        print(f"  Kalshi games: {len(kalshi_games)}")
        print(f"  Successful matches: {len(aligned_games)}")
        print(f"  Match rate: {len(aligned_games)/max(len(pinnacle_games),1)*100:.1f}%")
        print()
        
        # Show successful matches
        if aligned_games:
            print("4. SUCCESSFUL MATCHES")
            print("-" * 40)
            
            for i, match in enumerate(aligned_games, 1):
                pinnacle_data = match['pinnacle_data']
                kalshi_data = match['kalshi_data']
                confidence = match['match_confidence']
                
                print(f"MATCH {i}: {confidence:.1%} confidence")
                print(f"  Pinnacle: {pinnacle_data['away_team']} @ {pinnacle_data['home_team']}")
                print(f"            {pinnacle_data.get('game_time_display', 'N/A')}")
                print(f"  Kalshi:   {kalshi_data['away_team']} @ {kalshi_data['home_team']}")  
                print(f"            {kalshi_data.get('game_time_display', 'N/A')}")
                
                # Show reasons for match
                criteria = match['alignment_metadata']['matched_on']
                print(f"  Matched on: {', '.join(criteria)}")
                print()
        else:
            print("4. NO MATCHES FOUND")
            print("-" * 40)
            print("Possible reasons:")
            print("- Different team name formats")
            print("- Time differences too large")
            print("- No overlapping games")
            print("- Different sports detected")
        
        return aligned_games
    
    except Exception as e:
        print(f"ERROR: {e}")
        return []

def analyze_matching_issues(pinnacle_games, kalshi_games):
    """Analyze why games might not be matching"""
    print("5. MATCHING ANALYSIS")
    print("-" * 40)
    
    # Compare dates
    pinnacle_dates = set(game.get('game_date') for game in pinnacle_games if game.get('game_date'))
    kalshi_dates = set(game.get('game_date') for game in kalshi_games if game.get('game_date'))
    
    print(f"Pinnacle dates: {sorted(pinnacle_dates)}")
    print(f"Kalshi dates: {sorted(kalshi_dates)}")
    print(f"Common dates: {sorted(pinnacle_dates.intersection(kalshi_dates))}")
    print()
    
    # Compare teams
    pinnacle_teams = set()
    kalshi_teams = set()
    
    for game in pinnacle_games:
        pinnacle_teams.add(game.get('home_team'))
        pinnacle_teams.add(game.get('away_team'))
    
    for game in kalshi_games:
        kalshi_teams.add(game.get('home_team'))
        kalshi_teams.add(game.get('away_team'))
    
    common_teams = pinnacle_teams.intersection(kalshi_teams)
    
    print(f"Pinnacle teams: {sorted(list(pinnacle_teams)[:10])} ...")
    print(f"Kalshi teams: {sorted(list(kalshi_teams)[:10])} ...")
    print(f"Common teams: {sorted(list(common_teams))}")
    
    if not common_teams:
        print("WARNING: No common team names - matching will be difficult")
    elif len(common_teams) < 5:
        print("WARNING: Few common team names - matching may be limited")
    else:
        print("GOOD: Multiple common team names found")

def main():
    """Main test function"""
    script_path = "C:\\Users\\sammy\\Desktop\\development\\git\\claude-projects\\odds_api_pinnacle_kalshi\\test_game_alignment_fixed.py"
    
    print("GAME ALIGNMENT TEST WITH FIXED KALSHI DATES")
    print("Testing if Pinnacle and Kalshi games now align properly")
    print()
    
    # Test alignment
    aligned_games = test_alignment_with_fixed_dates('mlb')
    
    # If we have data, analyze matching issues
    try:
        pinnacle = PinnacleClient("keys/odds_api_key.txt")
        kalshi = KalshiClient("keys/kalshi_credentials.txt")
        
        pinnacle_raw = pinnacle.get_sports_odds('mlb')
        kalshi_raw = kalshi.search_sports_markets('mlb')
        
        if pinnacle_raw.get('success') and kalshi_raw.get('success'):
            pinnacle_games = pinnacle.normalize_pinnacle_data(pinnacle_raw, 15)
            kalshi_games = kalshi.normalize_kalshi_data(kalshi_raw, 15)
            
            analyze_matching_issues(pinnacle_games, kalshi_games)
    except:
        pass
    
    print()
    print("=" * 60)
    print("ALIGNMENT TEST COMPLETE")
    print("=" * 60)
    
    if aligned_games:
        print(f"SUCCESS: {len(aligned_games)} games successfully aligned!")
        print("The date fix appears to be working correctly.")
    else:
        print("ISSUE: No games were aligned.")
        print("Check the analysis above for potential causes.")
    
    print()
    print(f"Script path: {script_path}")

if __name__ == "__main__":
    main()