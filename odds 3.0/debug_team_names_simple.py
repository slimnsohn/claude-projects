"""
Simple debug script using the working slim viewers
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'prod_ready'))

from slim_game_viewer_fixed import SlimPinnacleClient, SlimKalshiClient

def debug_team_names():
    """Show actual team names from both platforms"""
    print("=== DEBUGGING TEAM NAMES ===")
    
    # Get Pinnacle data
    print("\n1. PINNACLE TEAM NAMES:")
    pinnacle = SlimPinnacleClient()
    pin_games = pinnacle.get_games('nfl')
    
    print(f"Pinnacle total games: {len(pin_games)}")
    for i, game in enumerate(pin_games[:3], 1):  # First 3 games
        print(f"  {i}. '{game['away']}' @ '{game['home']}'")
        print(f"     Game time: {game['game_time']}")
    
    # Get Kalshi data  
    print("\n2. KALSHI TEAM NAMES:")
    kalshi = SlimKalshiClient()
    kal_games = kalshi.get_games('nfl')
    
    print(f"Kalshi total games: {len(kal_games)}")
    for i, game in enumerate(kal_games[:3], 1):  # First 3 games
        print(f"  {i}. '{game['away']}' @ '{game['home']}'")
        print(f"     Game time: {game['game_time']}")
    
    # Show difference in naming
    if pin_games and kal_games:
        print("\n3. NAMING COMPARISON:")
        print("Pinnacle format:", pin_games[0]['away'], "@", pin_games[0]['home'])
        print("Kalshi format:", kal_games[0]['away'], "@", kal_games[0]['home'])

if __name__ == "__main__":
    debug_team_names()