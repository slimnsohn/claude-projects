"""
Debug Game Alignment Process
Shows exactly how games are matched between Pinnacle and Kalshi
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

from pinnacle_client import PinnacleClient
from kalshi_client import KalshiClientUpdated as KalshiClient
from data_aligner import GameMatcher
from datetime import datetime, timezone

def get_filtered_data(sport='mlb', time_buffer_minutes=15):
    """Get the filtered data from both platforms"""
    print("=" * 80)
    print(f"FETCHING {sport.upper()} DATA FROM BOTH PLATFORMS")
    print("=" * 80)
    
    # Get Pinnacle data
    print("Fetching Pinnacle data...")
    pinnacle_client = PinnacleClient("keys/odds_api_key.txt")
    pinnacle_raw = pinnacle_client.get_sports_odds(sport)
    
    if not pinnacle_raw.get('success'):
        print(f"❌ Pinnacle error: {pinnacle_raw.get('error')}")
        return [], []
    
    pinnacle_games = pinnacle_client.normalize_pinnacle_data(pinnacle_raw, time_buffer_minutes)
    print(f"✅ Pinnacle: {len(pinnacle_games)} games ready")
    
    # Get Kalshi data
    print("Fetching Kalshi data...")
    kalshi_client = KalshiClient("keys/kalshi_credentials.txt")
    kalshi_raw = kalshi_client.search_sports_markets(sport)
    
    if not kalshi_raw.get('success'):
        print(f"❌ Kalshi error: {kalshi_raw.get('error')}")
        return pinnacle_games, []
    
    kalshi_games = kalshi_client.normalize_kalshi_data(kalshi_raw, time_buffer_minutes)
    print(f"✅ Kalshi: {len(kalshi_games)} games ready")
    
    return pinnacle_games, kalshi_games

def show_detailed_game_list(games, platform_name):
    """Show detailed list of games for one platform"""
    print(f"\n{platform_name.upper()} GAMES AVAILABLE FOR MATCHING:")
    print("=" * 70)
    
    if not games:
        print("❌ NO GAMES AVAILABLE")
        return
    
    for i, game in enumerate(games, 1):
        home_team = game.get('home_team', 'N/A')
        away_team = game.get('away_team', 'N/A')
        game_time = game.get('game_time', 'N/A')
        game_time_display = game.get('game_time_display', 'N/A')
        game_date = game.get('game_date', 'N/A')
        sport = game.get('sport', 'N/A')
        
        print(f"{i:2d}. {away_team} @ {home_team}")
        print(f"    Sport: {sport}")
        print(f"    Date: {game_date}")
        print(f"    Time: {game_time} ({game_time_display})")
        
        # Show odds
        home_odds = game.get('home_odds', {}).get('american', 'N/A')
        away_odds = game.get('away_odds', {}).get('american', 'N/A')
        print(f"    Odds: {home_team} {home_odds} | {away_team} {away_odds}")
        
        # Show additional info
        game_id = game.get('game_id', 'N/A')
        print(f"    ID: {game_id}")
        
        # For Kalshi, show original title
        if 'kalshi' in game_id.lower():
            original_title = game.get('metadata', {}).get('original_title', '')
            if original_title:
                print(f"    Original: {original_title}")
        
        print()

def debug_matching_process(pinnacle_games, kalshi_games):
    """Show detailed matching process"""
    print("=" * 80)
    print("DETAILED GAME MATCHING PROCESS")
    print("=" * 80)
    
    if not pinnacle_games:
        print("❌ No Pinnacle games - cannot match")
        return
    
    if not kalshi_games:
        print("❌ No Kalshi games - cannot match")
        return
    
    # Initialize matcher
    matcher = GameMatcher(time_threshold_hours=6.0)  # Allow 6 hour time difference
    used_kalshi_indices = set()
    
    print(f"Matching {len(pinnacle_games)} Pinnacle games against {len(kalshi_games)} Kalshi markets...")
    print(f"Time threshold: 6 hours (to handle time differences)")
    print()
    
    matches_found = 0
    
    for p_idx, pinnacle_game in enumerate(pinnacle_games):
        print(f"🔍 PINNACLE GAME {p_idx + 1}: {pinnacle_game['away_team']} @ {pinnacle_game['home_team']}")
        print(f"   Time: {pinnacle_game.get('game_time_display', 'N/A')}")
        print(f"   Teams: {pinnacle_game['home_team']} vs {pinnacle_game['away_team']}")
        print()
        
        # Calculate match scores for all Kalshi games
        match_candidates = []
        
        for k_idx, kalshi_game in enumerate(kalshi_games):
            if k_idx in used_kalshi_indices:
                continue  # Already matched
            
            # Calculate match confidence
            confidence = matcher._calculate_match_confidence(pinnacle_game, kalshi_game)
            
            if confidence > 0.1:  # Only show candidates with some confidence
                match_candidates.append({
                    'index': k_idx,
                    'game': kalshi_game,
                    'confidence': confidence
                })
        
        # Sort by confidence
        match_candidates.sort(key=lambda x: x['confidence'], reverse=True)
        
        print(f"   📊 KALSHI CANDIDATES (showing top 5):")
        if not match_candidates:
            print(f"   ❌ No potential matches found")
        else:
            for j, candidate in enumerate(match_candidates[:5]):
                k_game = candidate['game']
                conf = candidate['confidence']
                k_idx = candidate['index']
                
                print(f"   {j+1:2d}. {k_game['away_team']} @ {k_game['home_team']} - {conf:.1%} confidence")
                print(f"       Time: {k_game.get('game_time_display', 'N/A')}")
                print(f"       Teams: {k_game['home_team']} vs {k_game['away_team']}")
                
                # Show why it matched (or didn't)
                reasons = []
                
                # Check team similarity
                team_sim = matcher._calculate_team_similarity(pinnacle_game, k_game)
                if team_sim > 0.5:
                    reasons.append(f"Team match: {team_sim:.1%}")
                
                # Check time proximity  
                time_sim = matcher._calculate_time_similarity(pinnacle_game, k_game)
                if time_sim > 0:
                    reasons.append(f"Time match: {time_sim:.1%}")
                
                # Check date match
                date_sim = matcher._calculate_date_similarity(pinnacle_game, k_game)
                if date_sim > 0:
                    reasons.append(f"Date match: {date_sim:.1%}")
                
                if reasons:
                    print(f"       Reasons: {', '.join(reasons)}")
                
                print()
        
        # Find best match
        best_match = None
        if match_candidates and match_candidates[0]['confidence'] >= 0.7:
            best_match = match_candidates[0]
            used_kalshi_indices.add(best_match['index'])
            matches_found += 1
            
            print(f"   ✅ MATCH FOUND: Kalshi game {best_match['index'] + 1}")
            print(f"      Confidence: {best_match['confidence']:.1%}")
        else:
            print(f"   ❌ NO MATCH: Best confidence was {match_candidates[0]['confidence']:.1%} (need 70%)" if match_candidates else "   ❌ NO MATCH: No candidates found")
        
        print("-" * 70)
        print()
    
    print(f"🎯 MATCHING SUMMARY:")
    print(f"   Pinnacle games: {len(pinnacle_games)}")
    print(f"   Kalshi games: {len(kalshi_games)}")
    print(f"   Successful matches: {matches_found}")
    print(f"   Match rate: {matches_found/len(pinnacle_games)*100:.1f}%")

def show_team_standardization_comparison(pinnacle_games, kalshi_games):
    """Show how team names are standardized"""
    print("\n" + "=" * 80)
    print("TEAM NAME STANDARDIZATION COMPARISON")
    print("=" * 80)
    
    # Collect all unique teams
    pinnacle_teams = set()
    kalshi_teams = set()
    
    for game in pinnacle_games:
        pinnacle_teams.add(game['home_team'])
        pinnacle_teams.add(game['away_team'])
    
    for game in kalshi_games:
        kalshi_teams.add(game['home_team'])
        kalshi_teams.add(game['away_team'])
    
    print(f"PINNACLE TEAMS ({len(pinnacle_teams)}):")
    for team in sorted(pinnacle_teams):
        print(f"  {team}")
    
    print(f"\nKALSHI TEAMS ({len(kalshi_teams)}):")
    for team in sorted(kalshi_teams):
        print(f"  {team}")
    
    # Show overlap
    common_teams = pinnacle_teams.intersection(kalshi_teams)
    pinnacle_only = pinnacle_teams - kalshi_teams
    kalshi_only = kalshi_teams - pinnacle_teams
    
    print(f"\nCOMMON TEAMS ({len(common_teams)}):")
    for team in sorted(common_teams):
        print(f"  ✅ {team}")
    
    print(f"\nPINNACLE ONLY ({len(pinnacle_only)}):")
    for team in sorted(pinnacle_only):
        print(f"  🔵 {team}")
    
    print(f"\nKALSHI ONLY ({len(kalshi_only)}):")
    for team in sorted(kalshi_only):
        print(f"  🔴 {team}")
    
    # Analysis
    print(f"\n📊 TEAM NAME ANALYSIS:")
    if len(common_teams) > 0:
        print(f"   ✅ {len(common_teams)} teams have identical names - good for matching")
    else:
        print(f"   ⚠️  No identical team names - matching will rely on aliases")
    
    if len(pinnacle_only) > 0 or len(kalshi_only) > 0:
        print(f"   ℹ️  Different team name formats detected")
        print(f"   ℹ️  Matching will use team alias system")

def main():
    """Main debug function"""
    print("GAME ALIGNMENT DEBUG TOOL")
    print("Shows exactly how Pinnacle and Kalshi games are matched")
    print("=" * 80)
    
    # Configuration
    sport = 'mlb'  # Change this to test other sports
    time_buffer_minutes = 15
    
    print(f"Configuration: {sport.upper()}, {time_buffer_minutes} minute buffer")
    print()
    
    # Get data from both platforms
    pinnacle_games, kalshi_games = get_filtered_data(sport, time_buffer_minutes)
    
    # Show detailed game lists
    show_detailed_game_list(pinnacle_games, "Pinnacle")
    show_detailed_game_list(kalshi_games, "Kalshi")
    
    # Show team standardization
    show_team_standardization_comparison(pinnacle_games, kalshi_games)
    
    # Debug the matching process
    debug_matching_process(pinnacle_games, kalshi_games)
    
    print("\n" + "=" * 80)
    print("GAME ALIGNMENT DEBUG COMPLETE")
    print("=" * 80)
    print("\nKEY INSIGHTS:")
    print("• Time differences of 5-10 minutes are handled by the 6-hour threshold")
    print("• Team matching uses aliases (e.g., 'Athletics' = 'A's' = 'OAK')")
    print("• Confidence threshold is 70% - lower matches are rejected")
    print("• Sport compatibility is checked first")
    print("\nIf matches are failing:")
    print("1. Check if team names are too different")
    print("2. Verify game times are within 6 hours")
    print("3. Confirm same sport on both platforms")
    print("4. Check if games are on the same date")

if __name__ == "__main__":
    main()