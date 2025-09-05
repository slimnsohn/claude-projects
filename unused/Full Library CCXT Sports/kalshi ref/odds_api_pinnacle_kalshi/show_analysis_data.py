"""
Simple Script to Show Exact Data Being Analyzed
Shows Pinnacle and Kalshi data after live game filtering
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

from pinnacle_client import PinnacleClient
from kalshi_client import KalshiClientUpdated as KalshiClient
from datetime import datetime, timezone, timedelta

def show_pinnacle_data(sport='mlb', time_buffer_minutes=15):
    """Show exactly what Pinnacle data will be analyzed"""
    print("=" * 80)
    print(f"PINNACLE {sport.upper()} DATA (After Live Game Filtering)")
    print("=" * 80)
    
    try:
        client = PinnacleClient("keys/odds_api_key.txt")
        
        # Step 1: Get raw data
        print(f"Step 1: Fetching raw {sport} odds from Pinnacle...")
        raw_data = client.get_sports_odds(sport)
        
        if not raw_data.get('success'):
            print(f"❌ ERROR: {raw_data.get('error')}")
            return
        
        raw_games = raw_data.get('data', [])
        print(f"✅ Raw games found: {len(raw_games)}")
        
        # Step 2: Apply normalization with live game filtering
        print(f"Step 2: Applying {time_buffer_minutes}-minute buffer filter...")
        filtered_games = client.normalize_pinnacle_data(raw_data, time_buffer_minutes)
        
        live_filtered = len(raw_games) - len(filtered_games)
        print(f"✅ Games after filtering: {len(filtered_games)}")
        print(f"📊 Live games filtered out: {live_filtered}")
        
        # Step 3: Show the actual data being analyzed
        print(f"\nACTUAL PINNACLE DATA BEING ANALYZED:")
        print("-" * 60)
        
        if not filtered_games:
            print("❌ NO GAMES AVAILABLE FOR ANALYSIS")
            print(f"   All {len(raw_games)} games were filtered out (too close to start time)")
            return
        
        for i, game in enumerate(filtered_games, 1):
            home_team = game['home_team']
            away_team = game['away_team']
            game_time = game.get('game_time_display', game.get('game_time', 'N/A'))
            home_odds = game['home_odds']['american']
            away_odds = game['away_odds']['american']
            
            print(f"{i:2d}. {away_team} @ {home_team}")
            print(f"    Time: {game_time}")
            print(f"    Odds: {home_team} {home_odds:+d} | {away_team} {away_odds:+d}")
            print(f"    ID: {game['game_id']}")
            print()
        
        return filtered_games
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return []

def show_kalshi_data(sport='mlb', time_buffer_minutes=15):
    """Show exactly what Kalshi data will be analyzed"""
    print("=" * 80)
    print(f"KALSHI {sport.upper()} DATA (After Live Game Filtering)")
    print("=" * 80)
    
    try:
        client = KalshiClient("keys/kalshi_credentials.txt")
        
        # Step 1: Search for sports markets
        print(f"Step 1: Searching for {sport} markets on Kalshi...")
        raw_data = client.search_sports_markets(sport)
        
        if not raw_data.get('success'):
            print(f"❌ ERROR: {raw_data.get('error')}")
            return
        
        raw_markets = raw_data.get('data', [])
        print(f"✅ Raw markets found: {len(raw_markets)}")
        
        # Show sport breakdown
        sport_counts = raw_data.get('sport_counts', {})
        if sport_counts:
            print(f"📊 Sport breakdown: {sport_counts}")
        
        # Step 2: Apply normalization with live game filtering
        print(f"Step 2: Applying {time_buffer_minutes}-minute buffer filter...")
        filtered_games = client.normalize_kalshi_data(raw_data, time_buffer_minutes)
        
        live_filtered = len(raw_markets) - len(filtered_games)
        print(f"✅ Markets after filtering: {len(filtered_games)}")
        print(f"📊 Live markets filtered out: {live_filtered}")
        
        # Step 3: Show the actual data being analyzed
        print(f"\nACTUAL KALSHI DATA BEING ANALYZED:")
        print("-" * 60)
        
        if not filtered_games:
            print("❌ NO MARKETS AVAILABLE FOR ANALYSIS")
            if len(raw_markets) > 0:
                print(f"   All {len(raw_markets)} markets were filtered out (too close to start time)")
            else:
                print(f"   No {sport.upper()} markets found on Kalshi today")
            return
        
        for i, game in enumerate(filtered_games, 1):
            home_team = game['home_team']
            away_team = game['away_team']
            game_time = game.get('game_time_display', game.get('game_time', 'N/A'))
            home_odds = game['home_odds']['american']
            away_odds = game['away_odds']['american']
            original_title = game['metadata']['original_title']
            
            print(f"{i:2d}. {away_team} @ {home_team}")
            print(f"    Time: {game_time}")
            print(f"    Odds: {home_team} {home_odds:+d} | {away_team} {away_odds:+d}")
            print(f"    Title: {original_title}")
            print(f"    ID: {game['game_id']}")
            print()
        
        return filtered_games
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return []

def show_time_filtering_details(time_buffer_minutes=15):
    """Show details about time filtering"""
    print("=" * 80)
    print("LIVE GAME FILTERING DETAILS")
    print("=" * 80)
    
    now = datetime.now(timezone.utc)
    cutoff_time = now + timedelta(minutes=time_buffer_minutes)
    
    print(f"Current time (UTC): {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Time buffer: {time_buffer_minutes} minutes")
    print(f"Cutoff time: {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("FILTERING RULES:")
    print(f"✅ INCLUDE: Games starting AFTER {cutoff_time.strftime('%H:%M')} UTC")
    print(f"❌ EXCLUDE: Games starting BEFORE {cutoff_time.strftime('%H:%M')} UTC")
    print(f"❌ EXCLUDE: Games already in progress")
    print(f"❌ EXCLUDE: Games with unparseable start times")
    print()

def show_comparison_summary(pinnacle_games, kalshi_games):
    """Show comparison between the two datasets"""
    print("=" * 80)
    print("DATA COMPARISON SUMMARY")
    print("=" * 80)
    
    print(f"Pinnacle games ready for analysis: {len(pinnacle_games)}")
    print(f"Kalshi markets ready for analysis: {len(kalshi_games)}")
    
    if len(pinnacle_games) == 0 and len(kalshi_games) == 0:
        print("\n❌ NO DATA AVAILABLE FOR ANALYSIS")
        print("   Reasons could be:")
        print("   - No games scheduled in the next few hours")
        print("   - All games are live or starting soon")
        print("   - API connection issues")
        print("   - Sport not available on one or both platforms")
        return
    
    if len(pinnacle_games) == 0:
        print("\n⚠️  NO PINNACLE DATA - Analysis will fail")
        return
    
    if len(kalshi_games) == 0:
        print("\n⚠️  NO KALSHI DATA - Analysis will fail")
        return
    
    print(f"\n✅ BOTH PLATFORMS HAVE DATA - Analysis can proceed")
    print(f"   Maximum possible game matches: {min(len(pinnacle_games), len(kalshi_games))}")
    
    # Show team matching preview
    print(f"\nTEAM MATCHING PREVIEW:")
    print("-" * 40)
    pinnacle_teams = set()
    kalshi_teams = set()
    
    for game in pinnacle_games[:5]:  # First 5 games
        pinnacle_teams.add(game['home_team'])
        pinnacle_teams.add(game['away_team'])
        
    for game in kalshi_games[:5]:
        kalshi_teams.add(game['home_team'])  
        kalshi_teams.add(game['away_team'])
    
    common_teams = pinnacle_teams.intersection(kalshi_teams)
    print(f"Sample Pinnacle teams: {list(pinnacle_teams)[:8]}")
    print(f"Sample Kalshi teams: {list(kalshi_teams)[:8]}")
    print(f"Teams in both platforms: {list(common_teams)}")
    
    if common_teams:
        print("✅ Team overlap found - games may match")
    else:
        print("⚠️  No obvious team overlap - matching may be difficult")

def main():
    """Main function to show all analysis data"""
    print("ANALYSIS DATA VIEWER")
    print("Shows exactly what data main_system.py will analyze")
    print("=" * 80)
    
    # Configuration (match main_system defaults)
    sport = 'mlb'  # Change this to test other sports: nfl, nba, nhl
    time_buffer_minutes = 15  # Match main_system default
    
    print(f"CONFIGURATION:")
    print(f"Sport: {sport.upper()}")
    print(f"Time buffer: {time_buffer_minutes} minutes")
    print()
    
    # Show filtering details
    show_time_filtering_details(time_buffer_minutes)
    
    # Get Pinnacle data
    pinnacle_games = show_pinnacle_data(sport, time_buffer_minutes)
    
    print("\n")
    
    # Get Kalshi data  
    kalshi_games = show_kalshi_data(sport, time_buffer_minutes)
    
    print("\n")
    
    # Show comparison
    show_comparison_summary(pinnacle_games or [], kalshi_games or [])
    
    print("\n" + "=" * 80)
    print("ANALYSIS DATA REVIEW COMPLETE")
    print("=" * 80)
    print("\nThis is the EXACT data that main_system.py will use for analysis.")
    print("You can now run main_system.py and expect it to work with this data.")
    print("\nTo test with different sports, change the 'sport' variable at the top of main().")
    print("Available sports: mlb, nfl, nba, nhl, college_football, college_basketball")

if __name__ == "__main__":
    main()